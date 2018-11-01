from django.shortcuts import render
from . import models as tmd
from . import dbtools
from datetime import datetime
import time
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
# Create your views here.

dbrefreshed = False

def trade_report(request):
	global dbrefreshed
	if dbrefreshed == False:
		dbtools.refresh_k_data('k_bfq',)
		dbrefreshed = True
	note = tmd.Note.objects.filter()
	data = {}
	try:
		st_date = request.GET['st_date']
		ed_date = request.GET['ed_date']
		r_name = request.GET['r_name']
		data['st_date'] = st_date
		data['ed_date'] = ed_date
		data['r_name'] = r_name

	except BaseException as e:
		print(e)
	data['note'] = note
	#保存页面数据

	return render(request, 'tshare/trade_report.html',data)
	
def trade_detail(request,r_code):

	#store_k_data to tmp table
	dbtools.storekdata(r_code)
	ori_data = tmd.OriginalTradeData.objects.filter(code = r_code)
	k_data = tmd.K_days.objects.filter(code = r_code)
	note = tmd.Note.objects.filter(t_code = r_code)
	note = note.filter(t_type = "operation")
	try:
		st_date = request.GET['st_date']
		if st_date != "":
			st_date_dtm = datetime.strptime(st_date, "%Y-%m-%d")
			ori_data = ori_data.filter(date__gte = st_date_dtm)
	except BaseException as e:
		print(e)
		
	try:
		ed_date = request.GET['ed_date']
		if ed_date != "":
			ed_date_dtm = datetime.strptime(ed_date, "%Y-%m-%d") 
			ori_data = ori_data.filter(date__lte = ed_date_dtm)
	except BaseException as e:
		print(e)
		
	data = {}
	data['ori_data'] = ori_data;
	data['r_code'] = r_code
	data['k_data'] = k_data
	data['r_name'] = ori_data[1].name
	data['note'] = note
	return render(request, 'tshare/trade_detail.html',data)

def all_note(request):
	data = {}
	note = tmd.Note.objects.all()
	data['note'] = note
	return render(request, 'tshare/all_note.html',data)
		
def add_note(request):
	r_date = request.GET['r_date']
	r_name = request.GET['r_name']
	r_code = request.GET['r_code']
	r_type = request.GET['r_type']
	r_url = request.GET['r_url']
	r_time = time.time()
	r_content = request.GET['r_content']
	
	tmd.Note.objects.create(t_stamp = r_time, t_date = r_date, t_name = r_name,t_code = r_code,t_type = r_type, t_content = r_content)
	
	return HttpResponseRedirect(r_url)

	
def k_data_json(request,r_code):

	#store_k_data to tmp table
	dbtools.storekdata(r_code)
	k_data = tmd.K_days.objects.filter(code = r_code)
	k_list = []
	for i in k_data:
		k_list.append([str(i.date),i.open,i.close,i.low,i.high,i.volume])
		
	return JsonResponse(k_list, safe=False)

def trade_data_json(request):

	#store_k_data to tmp table
	stat_data = tmd.StatisticTradeData.objects.all().order_by('o_date')
	
	#买入时间大于等于st_date
	try:
		st_date = request.GET['st_date']
		if st_date != "":
			st_date_dtm = datetime.strptime(st_date, "%Y-%m-%d")
			stat_data = stat_data.filter(i_date__gte = st_date_dtm)
	except BaseException as e:
		print(e)
	
	#卖出时间小于等于ed_date	
	try:
		ed_date = request.GET['ed_date']
		if ed_date != "":
			ed_date_dtm = datetime.strptime(ed_date, "%Y-%m-%d") 
			stat_data = stat_data.filter(o_date__lte = ed_date_dtm)
	except BaseException as e:
		print(e)
	
	try:
		r_name = request.GET['r_name']
		if r_name != "":
			stat_data = stat_data.filter(name = r_name)
	except BaseException as e:
		print("r_name:")
		print(e)
		
	stat_list = []
	for i in stat_data:
		stat_list.append([i.code,i.name,str(i.i_date),str(i.o_date),i.i_total,i.time,i.earning,i.pct])
	return JsonResponse(stat_list, safe=False)