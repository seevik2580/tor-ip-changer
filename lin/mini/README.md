# tor-ip-changer linux version
request new identity every X seconds interval using TOR client

dependency:   curl, netcat, tor

install dependency:   
`sudo apt-get install -y tor curl`

usage:  
`chmod +x ipchanger`

`tor -f torrc`   OR    `tor --HashedControlPassword "" --ControlPort 9051 --SocksPort 9050`

### change ip every 10 seconds
`while true;do ./ipchanger;sleep 10;done`

!!!iam not responsible for anything what you will do with this program, or for any other s**ts !!!
it is for education purposes only
