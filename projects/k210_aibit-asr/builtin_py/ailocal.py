import KPU as kpu
import lcd
import time
import gc

try:
    del model
except Exception:
    pass
try:
    del classifier
except Exception:
    pass
gc.collect()
lcd.init()

class_num = 0
sample_num = 0
classifier=None

def loading(path):
    global class_num
    global sample_num
    global classifier
    
    model = kpu.load(0x300000)
    classifier, class_num, sample_num = kpu.classifier.load(model,path)
    
def training(class_names,sample_numd,save):
    global class_num
    global sample_num
    global classifier
    
    import image,sensor,board
    
    key = board.pin(9, board.GPIO.IN, board.GPIO.PULL_UP)
    model = kpu.load(0x300000)
    class_num = len(class_names)
    sample_num = class_num*sample_numd
    classifier = kpu.classifier(model, class_num, sample_num) 
    
    cap_num = 0
    train_status = 0
    last_cap_time = 0
    last_btn_status = 1
    
    while 1:
        try:
            img=sensor.snapshot()
        except:
            raise("[AIBIT]camera not called")
        if key.value() == 0:
            time.sleep_ms(30)
            if key.value() == 0 and (last_btn_status == 1) and (time.ticks_ms() - last_cap_time > 500):
                last_btn_status = 0
                last_cap_time = time.ticks_ms()
                if cap_num < class_num:
                    index = classifier.add_class_img(img)
                    cap_num += 1
                    print("add class image:", index)
                elif cap_num < class_num + sample_num:
                    index = classifier.add_sample_img(img)
                    cap_num += 1
                    print("add sample image:", index)
            else:
                img.draw_string(0,0,"Please A-key release",(255,0,0),2,mono_space=0)
        else:
            time.sleep_ms(30)
            if key.value() == 1 and (last_btn_status == 0):
                last_btn_status = 1
            if cap_num < class_num:
                img.draw_string(0,0, "Press A-key: "+class_names[cap_num],(255,0,0),2,mono_space=0)
            elif cap_num < class_num + sample_num:
                img.draw_string(0,0,  "Press A-key: NO.{}".format(cap_num-class_num),(255,0,0),2,mono_space=0)
                       
        if cap_num >= class_num + sample_num:
            print("start train")
            classifier.train()
            img.draw_string(60,88,"Training...",(255,0,0),4,mono_space=0)
            lcd.display(img)   
            time.sleep_ms(1000)   
            print("train end") 
            img = image.Image()
            img.draw_string(80,88,"Train OK",(255,0,0),4,mono_space=0)  
            lcd.display(img) 
            classifier.save(save) 
            print("train save")    
            break
                            
        lcd.display(img)                    
                
def predict(img,class_names):   
    try:
        res_index, min_dist = classifier.predict(img)
        return (class_names[res_index],99-min_dist)
    except Exception as e:
        raise("[AIBIT] predict err:", e)        