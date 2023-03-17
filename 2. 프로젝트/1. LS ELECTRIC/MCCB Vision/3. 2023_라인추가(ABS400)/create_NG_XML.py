import os, glob
import sys
# from lxml import etree
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import cv2
from datetime import datetime, timedelta


## 라인 리스트
## 추가 라인이 적용될 경우 하기 리스트에 라인 명을 추가해줘야함
## 라인명은 반드시 Blob의 라인 폴더 명과 일치해야함

#line_list = ['ABH125c_1', 'ABH250c_1', 'ABH125c_2', 'ABH250c_2']

## 신규 확장 라인 400/800 2개 추가 (라인명 확인 필요)
line_list = ['ABH125c_1', 'ABH250c_1', 'ABH125c_2', 'ABH250c_2','ABS400c']

## D-1 날짜
## D-1 데이터를 배치로 가져오기 때문에 var1 는 일반적으로 1
## 변수에 따라 D-n 의 데이터를 가져올 수 있음
var1 = sys.argv[1]
# var1 = 0
day_var = float(var1)
yesterday = datetime.now() - timedelta(days=day_var)
check_dt = yesterday.strftime('%Y%m%d')
check_mon = check_dt[:-2]

# samba 경로
origin_path = '/data/mccb'

# ======================================================================================================================
# ======================================================================================================================
## 각 NG 이미지에 해당하는 XML 파일을 맵핑하고, XML 파일이 존재하는 NG파일만 추출

def get_png_list(ng_path, xml_path):
    # NG 이미지(png)
	png_path_list = []
	xml_path_list = []
	for root, dirs, files in os.walk(ng_path):
		if files:
			condition = check_dt + '*.*.*.*.png'
			condition_path = os.path.join(root, condition)
			ng_files = glob.glob(condition_path)

			for file in ng_files:
				png_path_list.append(file.replace("\\", "/"))

	png_df = pd.DataFrame({'png_path': png_path_list})
	png_df['png_name'] = [x.split('/')[-1] for x in png_df['png_path']]

    # 라벨 정보(xml)
	for root, dirs, files in os.walk(xml_path):
		if files:
			condition = check_dt + '*.*.*.xml'
			condition_path = os.path.join(root, condition)
			xml_files = glob.glob(condition_path)
			for file in xml_files:
				xml_path_list.append(file.replace("\\", "/"))

	xml_df = pd.DataFrame({'xml_path': xml_path_list})
	xml_df['xml_name'] = [x.split('/')[-1] for x in xml_df['xml_path']]
	xml_df['png_name'] = [x.replace('.xml', '.NG.png') for x in xml_df['xml_name']]

    # # xml 파일이 있는 png만 추출
	png_df = pd.merge(png_df, xml_df, on='png_name', how='inner')
	return png_df

def img_bounding(df, rst_save_path):

	png_path = df['png_path'].tolist()
	png_name = df['png_name'].tolist()
	xml_path = df['xml_path'].tolist()
	xml_name = df['xml_name'].tolist()

	clear_num = 0
    # png 파일 하나씩 처리
	for one_png_path, one_png_name, one_xml_path, one_xml_name in zip(png_path, png_name, xml_path, xml_name):

        # 기본 정의 -----------------------------------------------------------------------------------------
 		# 색, 선 두께, 폰트 크기 정의
		colors = [(95,253,239),  # yellow 
					(0,17,255)]    # red (하이라이트)
            
		thickness = 4
		fontScale = 1

        # XML -----------------------------------------------------------------------------------------------
        # 이미지 1장당 불량 영역이 1개 이상이므로 리스트 생성
		xml_defect_class, xml_xmin, xml_ymin, xml_xmax, xml_ymax = [], [], [], [], []

        # xml 파일 불러오기
		content_xml = one_xml_path

		# tree = ET.ElementTree(ET.fromstring(content_xml))
		
		tree = ET.parse(content_xml)
		note = tree.getroot()

        # 파싱: 불량 유형
		for element in note.findall("object"):
			xml_defect_class.append(element.findtext("name"))

        # 파싱: 불량 영역 좌표
		for element in note.iter("bndbox"):
			xml_xmin.append(int(element.findtext("xmin")))
			xml_ymin.append(int(element.findtext("ymin")))
			xml_xmax.append(int(element.findtext("xmax")))
			xml_ymax.append(int(element.findtext("ymax")))

        # 결과 저장 -------------------------------------------------------------------------------------------
        # 이미지(1장)에 대해 n개 하이라이트 영역 그리기
		for i in range(len(xml_ymin)) : 
			# PNG -----------------------------------------------------------------------------------------------
			# 이미지 불러오기
			byte = one_png_path
			image = cv2.imread(byte, cv2.IMREAD_COLOR)
			image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

			# 그리기 --------------------------------------------------------------------------------------------
			# 이미지(1장)에 대한 불량영역(n개) 하나씩 처리
			for c, top, left, bottom, right in zip(xml_defect_class, xml_ymin, xml_xmin, xml_ymax, xml_xmax):
				try :
					
					# 좌표 지정
					top = max(0, np.floor(top + 0.5).astype('int32'))
					left = max(0, np.floor(left + 0.5).astype('int32'))
					bottom = min(image.shape[0], np.floor(bottom + 0.5).astype('int32'))  # y
					right = min(image.shape[1], np.floor(right + 0.5).astype('int32'))  # x

					# 불량영역 그리기
					cv2.rectangle(image, (left, top), (right, bottom), colors[0], thickness)
					# 불량유형 작성하기 (한글명 출력)  -- 나중에 필요할 시 사용
					#(text_width, text_height) = ImageFont.truetype("/NanumFont/NanumGothicBold.ttf", 50).getsize(class_name[c][0])
					#cv2.rectangle(image, (left, top), (left+text_width, top-text_height-5), colors[0], thickness=cv2.FILLED)
					#pill_image = Image.fromarray(image)
					#draw = ImageDraw.Draw(pill_image)
					#draw.text((left, top-text_height-5), class_name[c][0], font=ImageFont.truetype("/NanumFont/NanumGothicBold.ttf", 50), fill=(0,0,0))
					#image = cv2.cvtColor(cv2.cvtColor(np.array(pill_image), cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2RGB)

				except:
					continue
						
				# 하이라이트 좌표 지정
				top_highlight = max(0, np.floor(xml_ymin[i] + 0.5).astype('int32'))
				left_highlight = max(0, np.floor(xml_xmin[i] + 0.5).astype('int32'))
				bottom_highlight = min(image.shape[0], np.floor(xml_ymax[i] + 0.5).astype('int32')) # y
				right_highlight = min(image.shape[1], np.floor(xml_xmax[i] + 0.5).astype('int32'))   # x
				
				# 하이라이트 (red)
				cv2.rectangle(image, (left_highlight, top_highlight), (right_highlight, bottom_highlight), colors[1], thickness)    
				# 하이라이트 부분 불량유형 작성하기 (한글명 출력)  -- 나중에 필요할 시 사용   
				#(text_width_highlight, text_height_highlight) = ImageFont.truetype("/NanumFont/NanumGothicBold.ttf", 50).getsize(class_name[xml_defect_class[i]][0])
				#cv2.rectangle(image, (left_highlight, top_highlight), (left_highlight+text_width_highlight, top_highlight-text_height_highlight-5), colors[1], thickness=cv2.FILLED)
				#pill_image = Image.fromarray(image)
				#draw = ImageDraw.Draw(pill_image)
				#draw.text((left_highlight, top_highlight-text_height_highlight-5), class_name[xml_defect_class[i]][0], font=ImageFont.truetype("/NanumFont/NanumGothicBold.ttf", 50), fill=(0,0,0))
				#image = cv2.cvtColor(cv2.cvtColor(np.array(pill_image), cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2RGB)

			# 결과 저장 -------------------------------------------------------------------------------------------
			
			deft_type = str(xml_defect_class[i])
			box_xy = str(xml_xmin[i]) + '_' + str(xml_ymin[i]) + '_' + str(xml_xmax[i]) + '_' + str(xml_ymax[i]) 
			side = one_png_name.split('.')[2]
            
			rst_name = rst_save_path + '/' + side + '/' + one_png_name[:one_png_name.find('(')] + '.' + side + '.' + deft_type + '.' + box_xy + '.jpg'

			_, img_rst = cv2.imencode('.jpg', image)
			bytes_rst = img_rst.tobytes()

			os.makedirs(f'{rst_save_path}/{side}', exist_ok=True)

			# 저장 
			cv2.imwrite(rst_name, image)
	
			clear_num += 1

	#print(datetime.now())
	print('전체(NG) : ' + str(len(png_path)) + '개\n'
          '처리 완료(NG_XML) : ' + str(clear_num) + '개\n')

# ======================================================================================================================
# ======================================================================================================================
## 각 라인 별로 수행

for line in line_list:
	#print(datetime.now())
	print('\n>> '+ check_dt +' '+ line + ' : 시작')

	# raw 파일 경로 지정
	ng_path = origin_path + '/' + line + '/NG/' + check_mon + '/'
	xml_path = origin_path + '/' + line + '/XML/' + check_mon + '/'

    # PNG 이미지 & XML 파일 경로 지정
	# png_import_path = line + '/NG/' + check_mon
	# xml_import_path = line + '/XML/' + check_mon

	# print(line+ ' : PNG 이미지 & XML 파일 경로 지정 완료')

    # 결과 JPG 이미지 저장 경로 지정

	rst_save_path = origin_path + '/' +line + '/NG_XML/' + check_mon 
	os.makedirs(rst_save_path, exist_ok=True)

	f_condition = '/' + check_dt + '_'

	print(line+ ' : 결과 JPG 이미지 저장 경로 지정 완료')
	
	try:
	# 지정 경로의 파일 목록 가져오기
		png_df = get_png_list(ng_path, xml_path)

		if not png_df.empty :
	# 처리
			img_bounding(png_df, rst_save_path)
		else : 
			print(line + ' png_df is empty')

	except Exception as e:
		print(line+' exception : '+ str(e))
		continue
