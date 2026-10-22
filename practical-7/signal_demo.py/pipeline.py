import subprocess 

p1 = subprocess.Popen(["ls"], stdout=subprocess.PIPE)
p2 = subprocess.Popen(["grep","py"], stdin=p1.stdout, stdout=subprocess.PIPE, text=True)
p1.stdout.close()
out,_=p2.communicate()
p1.wait()
print(out)
