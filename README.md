# KRMESR  
  
超解像の使い方  
cat imagelist | python image_db.py                 #学習DBの作成  
python dbsr.py input_image.png output_image.png    #超解像処理  
  
  
SSIMによる評価  
cd iqa  
python compare_ssim.py image1.png image2.png  

