pyPadWorm
===================
update: 2017/09/22

This is a web worm for http://pad.skyozora.com/ 战友网 pet data collecting.
* python 3.7.0
* Beautifulsoup 4.2
### Description
* pyPadWorm is main srcipt for thread control, pet data saving and download list control.
* singlepage is for single page data downloading and it is called by pyPadWorm
* data organization: all data are saved in DST_SRC(default: dst, defined in pyPadWorm).
    * img data are saved in DST_SRC/head.
    * all pages are saved as html in DST_SRC/html
    * all pet data text are saved as txt in DST_SRC/.(group size is controlled by countstep)
    * log file records all error id and latest id

    