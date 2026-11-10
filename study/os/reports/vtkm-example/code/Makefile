obj-m += src/vtkm.o 

PWD := $(CURDIR) 
KDIR = /lib/modules/`uname -r`/build
EXTRA_CFLAGS = -Wall -g

all: vtkm-cli
	make -C $(KDIR) M=$(PWD) modules 

vtkm-cli: src/vtkm-cli.c src/vtkm_info.h
	gcc -Wall -Wextra -o vtkm-cli src/vtkm-cli.c

clean:
	make -C $(KDIR) M=$(PWD) clean
	rm -rf .cache vtkm-cli
