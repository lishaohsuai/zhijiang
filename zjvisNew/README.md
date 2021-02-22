## 依赖

运行前安装依赖：

- django `pip install Django`
- sklearn `conda install scikit-learn`或者`pip install scikit-learn`
- watchdog `pip install watchdog`

## 初始请求

在用户初始请求时，先请求等待页面`api/init?id=abc`其中参数`id`必须指定。

目前存在两个虚拟用户，id分别为`abc`和`def`，待后端载入完成指定用后的日志后，会自动跳转到该用户的类目信息。

## 类目信息

在前端程序启动时，先请求类目信息

请求api`api/getCategory`返回所有类目的标签，若日志中不存在某一类目信息，则返回空数组。

其中图graph不含tag信息，所以只返回`true`或空列表graph数据，超参数hparams同理。

返回数据格式如下：

```python
{
	.:    {
            scalar: {}, 
            media: {image: [], audio: [], text: []}, 
            statistic: {histogram: []}, 
            graph: [],
        	...
    	}
	train: {
            scalar: {epoch_loss: ["epoch_loss"], epoch_accuracy: ["epoch_accuracy"]}
            media: {image: [],…}
            statistic: {histogram: []}
            graph: ["true"]
            embedding: ["layer1/weights/Variable:0", "layer1/biases/Variable:0", …]
        	hparams: ["true"]
            custom: ["true"]
            }
	vgg: {
            scalar: {,…}
            media: {,…}
            statistic: {,…}
            graph: ["true"]
            embedding: []
        	hparams: []
            custom: ["true"]
		 }
}
```

## Scalar

根据tag，请求api：`api/scalar?run=.&tag=layer1/weights/summaries/mean`得到tag为`layer1/weights/summaries/mean`的数据

其中`run`与`tag`缺一不可

返回数据格式

```json
{
    "layer1/weights/summaries/mean": 
    [
    	{"wall_time": 1587176310.3070214, "step": 0, "value": -6.488610961241648e-05}, 
    						..., 
    	{"wall_time": 1587176425.348953, "step": 190, "value": -0.002039810409769416}
	]
}
```

随后随着数据量的增大，可能直接返回数组形式

```json
[
    [1587176310.3070214, 0, 0.12780000269412994],
 					...
 	[1587176425.348953, 190, 0.9401999711990356]
]
```

第一列是`wall_time`，第二列是`step`，第三列是`value`

## Image

由于前端不能处理图片，所以图片请求分为两个地址

图片的信息，请求api：`api/image?run=.&tag=input_reshape/input/image/0`可获得tag为`input_reshape/input/image/0`的图片信息

其中`run`与`tag`缺一不可

返回数据格式

```python
{
	"input_reshape/input/image/0": 
    [
	 	{"wall_time": 1587176317.1721938, "step": 10, "width": 28, "height": 28},
							...
	 	{"wall_time": 1587176425.348953, "step": 190, "width": 28, "height": 28}
    ]
}
```

拿到图片信息之后，再向后台请求图片

请求api：`api/image_raw?step=0&run=.&tag=input_reshape/input/image/0`可获得tag为`input_reshape/input/image/0`在第0代时候的图片

其中`step`、`run`与`tag`缺一不可

返回数据为图像本身

## Histogram

请求api：`api/histogram?run=.&tag=layer1/weights/summaries/histogram/histogram_summary`可获得tag为`layer1/weights/summaries/histogram/histogram_summary`的数据

其中`run`与`tag`缺一不可

返回数据格式

```json
{
   "layer1/activations/histogram_summary": 
	[
        [1587176317.1721938, 10, 0.0, 5.297224044799805, 
 			[[0.0, 0.17657413482666015, 2801825.0], 
  							...
  			 [5.120649909973144, 5.297224044799805, 2.0]]
         ],
							...
         [1587176425.348953, 190, 0.0, 6.3502936363220215, 
  			[[0.0, 0.2116764545440674, 3229943.0],
   							...
   			 [6.1386171817779545, 6.3502936363220215, 8.0]]
         ]
   	 ]
}
```

格式为

```json
[
    wall_time, step, min, max, 
	[[left, right, num],
			...
	 [left, right, num]]
]
```

## Distribution

请求api：`api/distribution?run=.&tag=layer1/weights/summaries/histogram/histogram_summary`可获得tag为`layer1/weights/summaries/histogram/histogram_summary`的数据

其中`run`与`tag`缺一不可

返回数据格式

```json
{"layer1/activations/histogram_summary":
 	[
    	[1587176310.3070214, 0, 
  			[[0, 0.0], [668, 0.020253705367086237],..., [10000, 4.971314430236816]]], 	
								...,
		[1587176419.1604998, 180, 
			[[0, 0.0], [668, 0.021192153914175192],..., [10000, 6.3502936363220215]]]
	]
}
```

格式为

```json
[
    wall_time, step,
		[[precentage, value],...,[precentage, value]]
]
```

precentage取值分别为0, 668, 1587, 3085, 5000, 6915, 8413, 9332, 10000 对应标准正态分布的百分位数。

## Text

请求api：`api/text?run=.&tag=custom_tag`可获得tag为`custom_tag`的数据

其中`run`与`tag`缺一不可（目前只有一个数据集，run可随意给，不进行校验）

返回数据格式

```json
{
    "custom_tag": 
 	[
 		{"wall_time": 1585807655.373738, "step": 0, 
 		 "value": "\u8fd9\u662f\u7b2c0\u53e5\u8bdd"},
 						..., 
		{"wall_time": 1585807656.327519, "step": 99, 
          "value": "\u8fd9\u662f\u7b2c99\u53e5\u8bdd"}
	]
}
```

## Audio

与图片类似，由于前端不能处理音频，所以音频请求分为两个地址

音频的信息，请求api：`api/audio?run=.&tag=waveform/audio_summary`可获得tag为`waveform/audio_summary`的音频信息

其中`run`与`tag`缺一不可（目前只有一个数据集，run可随意给，不进行校验）

返回数据格式

```json
{
    "waveform/audio_summary":
 	[
        {"wall_time": 1587475006.5022004, "step": 1, "label": "<p><em>Wave type:</em> <code>sine_wave</code>. <em>Frequency:</em> 448.98 Hz. <em>Sample:</em> 1 of 1.</p>", "contentType": "audio/wav"}, 
									...
	    {"wall_time": 1587475006.7304769, "step": 49, "label": "<p><em>Wave type:</em> <code>sine_wave</code>. <em>Frequency:</em> 880.00 Hz. <em>Sample:</em> 1 of 1.</p>", "contentType": "audio/wav"}
    ]
}
```

拿到音频信息之后，再向后台请求音频

请求api：`api/audio_raw?step=0&run=.&tag=waveform/audio_summary`和得到音频

其中`step`、`run`与`tag`缺一不可（目前只有一个数据集，run可随意给，不进行校验）

返回数据为音频本身

## Embedding

高维数据，由于降维过程较为费时，数据首先在后端进行处理，然后返回降维后的数据。

具体请求也是分为两步，第一步根据run和tag得到数据对应的step信息。

1. 请求指定训练集和标签，返回对应标签的所有step和shape

   请求`api` ：`/api/projector?run=train&tag=outputs`  其中 run 、tag 缺一不可 返回数据格式如下：

   ```python
   {
       "outputs": [0, 1, 2, ... ,n],
       "shape": [n,m]
   }
   ```

2. 请求指定训练集，标签，step,method,dims 返回降维后的数据和原始标签

   请求`api` ：`api/projector_data?run=train&tag=outputs&step=0&method=pca&dims=3` ，其中 run 、tag、step、method 缺一不可，dims默认为3。返回数据格式如下：

   ```python
   {
   		"0": [
               	# 降维后的数据
       			[[-1.5627723114617857, -3.9668523435955056, -0.18872563897943656],
   				[-1.5627723114617857, -3.9668523435955056, -0.18872563897943656],
   				[-1.5627723114617857, -3.9668523435955056, -0.18872563897943656],
   				              				.....
   				[-1.5627723114617857, -3.9668523435955056, -0.18872563897943656]],
               	# label信息
               	 [7,0,5,6,7,1,...,9,6,4]
               ]
   }
   ```
   
3. 请求指定训练集，标签，序号 返回原始训练数据

   请求`api` ：api/projector_sample?run=.&tag=outputs&index=0 ，其中 run 、tag、index 缺一不可。返回原始数据：图片，音频，文本

   

## Graph

由于计算图graph每个网络中只包含一个，所以请求时只需给定run参数即可

请求`api` ：`/api/graph?run=train`

返回run为train的计算图，数据格式为

```json
{
    "net": "[{...}]",  //graph计算图数据
 	"operator": "[...]" //操作结点分类数据
}
```

## exception

异常信息目前以projector的方式进行存取，标签信息请查看embedding（tag以 "**Variable:0**" 结尾）。

具体请求分为两步:

1. 请求指定训练集和标签，返回对应标签的所有step

   请求`api` ：`/api/exception?run=train&tag=layer1/weights/Variable:0`  其中 run 、tag 缺一不可 返回数据格式如下：

   ```python
   {
       "layer1/weights/Variable:0": [0, 1, 2, ... ,n]
   }
   ```

2. 请求指定训练集，标签，step 返回平铺后的异常数据

   请求`api` ：`api/exception_data?run=train&tag=layer1/weights/Variable:0&step=0` ，其中 run 、tag、step缺一不可，返回数据格式如下：

   ```python
   {
       	"0":[ 
               	[c1,c2],  # 平铺前的数据维度大小(长度不定)
               	min,
               	max,
               	mean,
               	[[-1.5627723114617857, -3.9668523435955056, -0.18872563897943656],
   				[-1.5627723114617857, -3.9668523435955056, -0.18872563897943656],
   				[-1.5627723114617857, -3.9668523435955056, -0.18872563897943656],
   				              				.....
   				[-1.5627723114617857, -3.9668523435955056, -0.18872563897943656]]
           	]
   }
   ```
   
   
   
3. 请求指定训练集，标签，step 返回异常数据的直方图信息

   请求`api` ：`api/exception_hist?run=train&tag=layer1/weights/Variable:0&step=0` ，其中 run 、tag、step缺一不可，返回数据格式如下

   ```python
   {
       	"0":[ 
               	min,
               	max,
               	[[left, right, count],
                    [left, right, count],
   					.....
   				[left, right, count]]
           	]
   }
   ```

## Hyperparam

请求api: `api/hyperparm?run=hparams`，可获得（如果有数据的话）run为hparams的超参数数据

返回数据格式：

```
{"hparamsInfo": [{groupid_1: 
                    {"hparams": [{"name": 超参数1, "data": 数据1}, ..., {"name": 超参数2, "data": 数据2}], 
				    "start_time_secs": 开始时间}
				 }
				,..., 
                 {groupid_n: 
                    {"hparams": [{"name": 超参数1, "data": 数据1}, ..., {"name": 超参数2, "data": 数据2}], // 多个超参数的名字与值
				    "start_time_secs": 开始时间}
				}], // 超参数信息，可能有多个
 "metrics": [{"tag": 量度1, "value": [值1, 值2, ...., 值n]},..., {"tag": 量度n, "value": [值1, 值2, ...., 值n]}]}
 //超参数的量度，可能有多个。适用于所有的超参数信息
```

例如train中的超参数数据为：

```
{"hparamsInfo": [{"3df0d7cf35bec5a33c9fe551db732c24df204d7886b226c5a41cce285d0d4fd5": 
                    {"hparams": [{"name": "num_units", "data": 32.0}, 
                                 {"name": "optimizer", "data": "sgd"}, 
                                 {"name": "dropout", "data": 0.2}], 
                    "start_time_secs": 1589421877.1109092}
                }], // 超参数信息，可能有多个
 "metrics": [{"tag": "accuracy", "value": [0.8216999769210815, 0.8241999745368958, 0.7746999859809875, 0.765999972820282, 0.8411999940872192, 0.8307999968528748, 0.7940999865531921, 0.7904999852180481]}]} //超参数的量度，可能有多个。适用于所有的超参数信息
```

## Axios 调用

1. 请求指定类型的tag (返回该类型下所有数据集的tag)

   ```js
   // Vue组件中测试代码
   this.$axios.get('http://127.0.0.1:8000/api/tags',{   //后台端口号，tags
               params:{
                 plugin: 'text'     //请求的类型，该示例为text
               }
             })
             .then((res) => {      // res.data 为返回的数据式
               ...
             })
   /* 
       res.data 返回的tags是一个字典，数据格式如下：run_n ：数据集的名字，tagn ：标签名
       {
           run_1:{layer1:[layer1/tag1,layer1/tag2,...,layer1/tagn]
           	  layer2:[layer2/tag1,layer2/tag2,...,layer2/tagn]},
           run_2:{layer1:[layer1/tag1,layer1/tag2,...,layer1/tagn]
           	  layer2:[layer2/tag1,layer2/tag2,...,layer2/tagn]},
                   ......
           run_n:{layer1:[layer1/tag1,layer1/tag2,...,layer1/tagn]
           	  layer2:[layer2/tag1,layer2/tag2,...,layer2/tagn]},
       }
   */
   ```

2. 请求指定run和tag的数据

```js
// Vue组件中的测试代码
this.$axios.get('http://127.0.0.1:8000/api/text', {  //后台端口号，请求类型：text (自行修改)
            params: {
              run: run_name,     //数据集
              tag: tag_name		//标签名
            }
          })
          .then((res) => {   // res.data 为返回指定标签的数据，数据格式见上述几种格式
                ...
              })
          })
```

