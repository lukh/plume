https://wiki.gentoo.org/wiki/Create_a_Public_Key_Infrastructure_Using_the_easy-rsa_Scripts

```
sudo apt install easy-rsa
ln -s /usr/share/easy-rsa/* ./
# create ./vars
./easyrsa init-pki
./easyrsa build-ca nopass
./easyrsa gen-req localhost nopass
./easyrsa sign-req server localhost

```
