#!/usr/bin/env python

'''
A simple Python wrapper for the bh_tsne binary that makes it easier to use it
for TSV files in a pipeline without any shell script trickery.

Note: The script does some minimal sanity checking of the input, but don't
    expect it to cover all cases. After all, it is a just a wrapper.

Example:

    > echo -e '1.0\t0.0\n0.0\t1.0' | ./bhtsne.py -d 2 -p 0.1
    -2458.83181442  -6525.87718385
    2458.83181442   6525.87718385

The output will not be normalised, maybe the below one-liner is of interest?:

    python -c 'import numpy;  from sys import stdin, stdout;
        d = numpy.loadtxt(stdin); d -= d.min(axis=0); d /= d.max(axis=0);
        numpy.savetxt(stdout, d, fmt="%.8f", delimiter="\t")'

Authors:     Pontus Stenetorp    <pontus stenetorp se>
             Philippe Remy       <github: philipperemy>
Version:    2016-03-08
'''

# Copyright (c) 2013, Pontus Stenetorp <pontus stenetorp se>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from os import devnull
from os.path import abspath, dirname, isfile, join as path_join
from platform import system
from shutil import rmtree
from struct import calcsize, pack, unpack
from subprocess import Popen
from sys import stderr
from tempfile import mkdtemp

import numpy as np

### Constants
IS_WINDOWS = True if system() == 'Windows' else False
BH_TSNE_BIN_PATH = path_join(dirname(__file__), 'tsne', 'bh_tsne.exe') if IS_WINDOWS else path_join(dirname(__file__),
                                                                                                    'tsne','bh_tsne')
assert isfile(BH_TSNE_BIN_PATH), ('Unable to find the bh_tsne binary in the '
                                  'same directory as this script, have you forgotten to compile it?: {}'
                                  ).format(BH_TSNE_BIN_PATH)
# Default hyper-parameter values from van der Maaten (2014)
# https://lvdmaaten.github.io/publications/papers/JMLR_2014.pdf (Experimental Setup, page 13)
DEFAULT_NO_DIMS = 2
INITIAL_DIMENSIONS = 50
DEFAULT_PERPLEXITY = 25
DEFAULT_THETA = 0.5
EMPTY_SEED = -1
DEFAULT_USE_PCA = True
DEFAULT_MAX_ITERATIONS = 50


###

def _read_unpack(fmt, fh):
    return unpack(fmt, fh.read(calcsize(fmt)))


# def _is_filelike_object(f):
#     try:
#         return isinstance(f, (file, io.IOBase))
#     except NameError:
#         # 'file' is not a class in python3
#         return isinstance(f, io.IOBase)


def init_bh_tsne(samples, workdir, no_dims=DEFAULT_NO_DIMS, initial_dims=INITIAL_DIMENSIONS,
                 perplexity=DEFAULT_PERPLEXITY,
                 theta=DEFAULT_THETA, randseed=EMPTY_SEED, verbose=False, use_pca=DEFAULT_USE_PCA,
                 max_iter=DEFAULT_MAX_ITERATIONS):
    if use_pca:
        samples = samples - np.mean(samples, axis=0)
        cov_x = np.dot(np.transpose(samples), samples)
        [eig_val, eig_vec] = np.linalg.eig(cov_x)

        # sorting the eigen-values in the descending order
        eig_vec = eig_vec[:, eig_val.argsort()[::-1]]

        if initial_dims > len(eig_vec):
            initial_dims = len(eig_vec)

        # truncating the eigen-vectors matrix to keep the most important vectors
        eig_vec = np.real(eig_vec[:, :initial_dims])
        samples = np.dot(samples, eig_vec)

    # Assume that the dimensionality of the first sample is representative for
    #   the whole batch
    sample_dim = len(samples[0])
    sample_count = len(samples)

    # Note: The binary format used by bh_tsne is roughly the same as for
    #   vanilla tsne
    with open(path_join(workdir, 'data.dat'), 'wb') as data_file:
        # Write the bh_tsne header
        data_file.write(pack('iiddii', sample_count, sample_dim, theta, perplexity, no_dims, max_iter))
        # Then write the data
        for sample in samples:
            data_file.write(pack('{}d'.format(len(sample)), *sample))
        # Write random seed if specified
        if randseed != EMPTY_SEED:
            data_file.write(pack('i', randseed))


def bh_tsne(workdir, verbose=False):
    # Call bh_tsne and let it do its thing
    with open(devnull, 'w') as dev_null:
        bh_tsne_p = Popen((abspath(BH_TSNE_BIN_PATH),), cwd=workdir,
                          # bh_tsne is very noisy on stdout, tell it to use stderr
                          #   if it is to print any output
                          stdout=stderr if verbose else dev_null)
        bh_tsne_p.wait()
        assert not bh_tsne_p.returncode, ('ERROR: Call to bh_tsne exited '
                                          'with a non-zero return code exit status, please ' +
                                          ('enable verbose mode and ' if not verbose else '') +
                                          'refer to the bh_tsne output for further details')

    # Read and pass on the results
    with open(path_join(workdir, 'result.dat'), 'rb') as output_file:
        # The first two integers are just the number of samples and the
        #   dimensionality
        result_samples, result_dims = _read_unpack('ii', output_file)
        # Collect the results, but they may be out of order
        results = [_read_unpack('{}d'.format(result_dims), output_file)
                   for _ in range(result_samples)]
        # Now collect the landmark data so that we can return the data in
        #   the order it arrived
        results = [(_read_unpack('i', output_file), e) for e in results]
        # Put the results in order and yield it
        results.sort()
        for _, result in results:
            yield result
        # The last piece of data is the cost for each sample, we ignore it
        # read_unpack('{}d'.format(sample_count), output_file)


def run_bh_tsne(data, no_dims=DEFAULT_NO_DIMS, perplexity=DEFAULT_PERPLEXITY, theta=DEFAULT_THETA,
                randseed=EMPTY_SEED, verbose=False, initial_dims=INITIAL_DIMENSIONS, use_pca=DEFAULT_USE_PCA,
                max_iter=DEFAULT_MAX_ITERATIONS):
    '''
    Run TSNE based on the Barnes-HT algorithm

    Parameters:
    ----------
    data: file or numpy.array
        The data used to run TSNE, one sample per row
    no_dims: int
    perplexity: int
    randseed: int
    theta: float
    initial_dims: int
    verbose: boolean
    use_pca: boolean
    max_iter: int
    '''
    # bh_tsne works with fixed input and output paths, give it a temporary
    #   directory to work in so we don't clutter the filesystem
    tmp_dir_path = mkdtemp()
    init_bh_tsne(data, tmp_dir_path, no_dims=no_dims, perplexity=perplexity, theta=theta, randseed=randseed, verbose=verbose,
                 initial_dims=initial_dims, use_pca=use_pca, max_iter=max_iter)
    res = []
    for result in bh_tsne(tmp_dir_path, verbose):
        sample_res = []
        for r in result:
            sample_res.append(r)
        res.append(sample_res)
    rmtree(tmp_dir_path)
    return np.array(res, dtype='float64')


def tsne(data, dimension=DEFAULT_NO_DIMS, randseed=EMPTY_SEED,perplexity =DEFAULT_PERPLEXITY):
    if len(data)<100:
        perplexity = int(0.1*len(data))
    result = run_bh_tsne(data, no_dims=dimension, initial_dims=len(data[0]), randseed=randseed,perplexity =perplexity )
    return result
