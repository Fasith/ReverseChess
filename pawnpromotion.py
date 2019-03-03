import Tkinter as tk
from Tkinter import *
import tkMessageBox



class pawnpromotiondialog:

    def __init__(self, parent,images):

        top = self.top = Toplevel(parent)
        top.configure(background='black')
        #top.geometry('100x800')
        Label(top,text="Congradulations you have a pawn promotion!",font=("bold italic", 15, "bold"),bg='black',fg='white',height=2).grid(padx=10,row=0,column=0)
        Label(top,text="Pick a piece",fg='white',font=("bold italic", 15, "bold"),height=2,bg='black').grid(padx=10,row=1,column=0)
        pieces_avail=['King','Queen','Knight','Bishop','Rook']
        k=2
        
        #photo2=PhotoImage(file="img/lackb.png")
        #print photo,photo2
        #button.config(image=photo,width="40",height="40",activebackground="black")

        for i,j in zip(pieces_avail,images):
            button = Button(top,command=lambda x=i:self.click(x),bg='#FFC300',image=j,width=500,height=64)#.config(image=photo,width="40",height="40",activebackground="black")
            button.grid(row=k,column=0)
            k=k+1
    def click(self,x):
    	if(x=='King'):
    		print 'King'
    	elif(x=='Queen'):
    		print 'Queen'
    	elif(x=='Knight'):
    	    print 'Knight'
        elif(x=='Bishop'):
    	    print 'Bishop'
        elif(x=='Rook'):
    	    print 'Rook'
    	self.top.destroy()
    


        #print "value is", self.e.get(),self.f.get(),self.g.get()

def main():
	root=tk.Tk()
	photoking=PhotoImage(file="img/blackk.png")
	photobishop=PhotoImage(file="img/blackb.png")
	photoknight=PhotoImage(file="img/blackn.png")
	photoqueen=PhotoImage(file="img/blackq.png")
	photorook=PhotoImage(file="img/blackr.png")
	images=[photoking,photoqueen,photoknight,photobishop,photorook]
	ppd=pawnpromotiondialog(root,images)
	root.configure(background='black')
	root.mainloop()
if __name__=='__main__':
	main()