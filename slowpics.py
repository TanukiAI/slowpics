import subprocess, json, os, glob, datetime, sys
from shutil import rmtree as rmdir
try:
	import requests
	from pyperclip import copy
	from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
	from clint.textui.progress import Bar as ProgressBar
except:
	print("ImportError!")
	print('Please run "py -3 -m pip install requests clint requests-toolbelt pyperclip --upgrade" in the console.')
	sys.exit()

#FFMPEG/FFPROBE
def pec(program):
	'''
	Program Exist Check
	'''
	try:
		subprocess.call(program, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
	except FileNotFoundError:
		print("You didn't install " + program + ". Please put in in PATH or in the current folder and restart the program...")
	except:
		raise
def gft(timed):
	'''
	Get Formatted Time
	'''
	#time.strftime('%H:%M:%S', time.gmtime(timed))
	return str(datetime.timedelta(seconds=timed))
pec("ffmpeg")
pec("ffprobe")

#Screenshots

v1 = input("Input the Videoname of Video 1: ")
if os.path.basename(v1) == v1:
	v1 = "./" + v1
v2 = input("Input the Videoname of Video 2: ")
if os.path.basename(v2) == v2:
	v2 = "./" + v2
try:
	duration = int(json.loads(subprocess.check_output(['ffprobe', '-i', v1, '-print_format', 'json', '-v', 'quiet', '-show_format', '-show_streams']))["format"]["duration"].split(".")[0])
except:
	raise

print("Video Duration: "+str(duration)+" seconds")
sc = int(input("How many Screenshots should be taken: ")) + 1
sctime = round(duration/sc)
print("A screenshot will be taken every "+ str(sctime) +" seconds")

v1dir = "_Video_1"
v2dir = "_Video_2"
for i in [v1dir,v2dir]:
	try:
		os.mkdir(i)
	except FileExistsError:
		if input("The folder " + i + " already exists. Should it be removed (y/n): ").lower() == "y":
			rmdir(i)
			os.mkdir(i)
		else:
			sys.exit()
print()
#Making Screenshots
t = 0
for loli in range(1,sc):
	t += sctime
	subprocess.call(['ffmpeg','-loglevel','error','-ss',gft(t),'-i',v1,'-vframes','1','-q:v','1','"./'+v1dir+'/screenshot_'+str(loli)+'.png"'])
	subprocess.call(['ffmpeg','-loglevel','error','-ss',gft(t),'-i',v2,'-vframes','1','-q:v','1','"./'+v2dir+'/screenshot_'+str(loli)+'.png"'])
	print("Created Screenshot "+str(loli))
v1files = glob.glob(v1dir+"/*.png")
v2files = glob.glob(v2dir+"/*.png")
print()
def create_callback(files):
	bar = ProgressBar(expected_size=files.len, filled_char='█')
	def callback(monitor):
		bar.show(monitor.bytes_read)
	return callback


s = requests.session()
s.get("https://slowpics.org/comparison")
collName = input("Please input a name for your collection: ")

fields={
"collectionName":collName,
"public":"false",
}

for i in range(len(v1files)):
	fields["comparisons["+str(i)+"].name"] = str(i+1)
	fields["comparisons["+str(i)+"].images[0].name"] = os.path.basename(v1files[i]).replace(".png","")
	fields["comparisons["+str(i)+"].images[0].file"] = (os.path.basename(v1files[i]),open(v1files[i],"rb"),"image/png")
	fields["comparisons["+str(i)+"].images[1].name"] = os.path.basename(v2files[i]).replace(".png","")
	fields["comparisons["+str(i)+"].images[1].file"] = (os.path.basename(v2files[i]),open(v2files[i],"rb"),"image/png")
files = MultipartEncoder(fields)
callback=create_callback(files)
monitor=MultipartEncoderMonitor(files, callback)

headers={
"Accept": "*/*",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
"Content-Length":str(files.len),
"Content-Type": monitor.content_type,
"Origin": "https://slowpics.org",
"Referer": "https://slowpics.org/comparison",
"Sec-Fetch-Mode": "cors",
"Sec-Fetch-Site": "same-origin",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
"X-XSRF-TOKEN": s.cookies.get_dict()["XSRF-TOKEN"]
}
print('Uploading pictures to SlowPics with Collectionname "'+collName+'".')
ComparisonURL = s.post("https://slowpics.org/api/comparison", data=monitor, headers=headers)

print("URL: https://slowpics.org/comparison/"+ComparisonURL.text)
copy("https://slowpics.org/comparison/"+ComparisonURL.text)
print("The URL has been copied to your clipboard.")