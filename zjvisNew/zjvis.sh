cd backend
python main.py --port=9898 >/dev/null 2>&1 &
cd ../parser_service
python master.py >/dev/null 2>&1 &
