## openplotter-sdr-ais

Get radio and AIS data in OpenPlotter using SDR devices

### Installing

#### For production

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production** and just install this app from *OpenPlotter Apps* tab.

#### For development

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **development**.

Clone the repository:

`git clone https://github.com/openplotter/openplotter-sdr-ais`

Make your changes and create the package:

```
cd openplotter-sdr-ais
dpkg-buildpackage -b
```

Install the package:

```
cd ..
sudo dpkg -i openplotter-sdr-ais_x.x.x-xxx_all.deb
```

Run:

`openplotter-sdr-ais`

Make your changes and repeat package and installation steps to test. Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://launchpad.net/~openplotter/+archive/ubuntu/openplotter).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1
