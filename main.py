import re,requests,time,os
import urllib.request
from moviepy.editor import *
from skimage.filters import gaussian

def blur(image):
    return gaussian(image.astype(float), sigma=4)

def download(url: str, dest_folder: str):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))


url='https://www.tiktok.com/api/recommend/item_list/?aid=1988&count=35'
req=requests.get(url)
data=req.headers['set-cookie']
msToken=re.search('msToken=(.*?)\;.*',data).group(1)
abck=re.search('.*\_abck=(.*?)\;.*',data).group(1)
bm_sz=re.search('.*bm\_sz=(.*?)\;.*',data).group(1)
req=requests.get(url,headers={
'cookie':'msToken='+msToken+'; _abck='+abck+'; bm_sz='+bm_sz+';s_v_web_id=verify_077f93acf1486ff1fc55ae8bc6160510;sessionid=da5fedc0df4a60a9e51f993d40315420;sessionid_ss=da5fedc0df4a60a9e51f993d40315420;tt-target-idc=alisg;'
})
arr=[]
for i,vid in enumerate(req.json()['itemList']):
    #print(vid['desc'])
    arr.append(vid['desc'])
    urllib.request.urlretrieve(vid['video']['downloadAddr'],'downloaded/'+str(i)+'.mp4')
    #print(vid['video']['downloadAddr'])
    if i==1:
        #final_clip=concatenate_videoclips([VideoFileClip("downloaded/9.mp4"),VideoFileClip("downloaded/10.mp4"),VideoFileClip("downloaded/11.mp4"),VideoFileClip("downloaded/8.mp4")],method='compose')
        #final_clip.write_videofile("my_stack1.mp4",audio_codec="aac")
        with VideoFileClip("my_stack1.mp4") as video:
            if video.aspect_ratio < 1.7:
                video.write_videofile(
                    "my_stack.mp4",audio_codec="aac",
                    ffmpeg_params=['-lavfi', '[0:v]scale=ih*16/9:-1,boxblur=luma_radius=min(h\,w)/20:luma_power=1:chroma_radius=min(cw\,ch)/20:chroma_power=1[bg];[bg][0:v]overlay=(W-w)/2:(H-h)/2,crop=h=iw*9/16']
                )
        #final_clip = clips_array([VideoFileClip("downloaded/0.mp4",audio=True),VideoFileClip("downloaded/1.mp4"),VideoFileClip("downloaded/2.mp4")])
        #final_clip.write_videofile("my_stack.mp4")
        print(arr)
        break
