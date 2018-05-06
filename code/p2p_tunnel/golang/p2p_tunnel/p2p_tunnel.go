package main

import "log"
import "flag"
import "fmt"
import "github.com/GarethNelson/go-stun/stun"
import "github.com/GarethNelson/water"
import "golang.org/x/crypto/pbkdf2"
import "crypto/sha1"

var verbose_mode = false

func nat_probe(server_addr string) {
     if(verbose_mode) {
        fmt.Println("Probing NAT setup...")
     }
     stun_client := stun.NewClient()
     stun_client.SetServerAddr(server_addr)
     stun_client.SetVerbose(verbose_mode)
     nat_type, host, err := stun_client.Discover()

     if err != nil {
        fmt.Println("Error occurred while probing NAT: ", err)
        return
     }

     if(verbose_mode) {
         fmt.Println("Detected NAT type: ",nat_type)
         fmt.Println("External IP:       ",host.IP())
         fmt.Println("External port:     ",host.Port())
     }
}

func open_tun() {
     config      := water.Config{DeviceType: water.TUN}
     tun_if, err := water.New(config)
     if err != nil {
        log.Fatal(err)
     }
     log.Printf("Opened TUN device: %s\n", tun_if.Name())
}

func derive_key(password string) {
     salt := []byte{0xFE,0xED,0xFA,0xCE,0xDE,0xAD,0xBE,0xEF} // this is obviously a terrible idea and would not happen in production code
     key  := pbkdf2.Key([]byte(password), salt, 16, 32, sha1.New)
}

func main() {
     stunServerPtr  := flag.String("stun-server",    "172.16.0.10:3478",         "STUN/TURN server to use")
     connectAddrPtr := flag.String("connect-address","172.16.0.2",               "Address of remote peer to attempt to connect to")
     passwordPtr    := flag.String("password",       "CorrectHorseBatteryStaple","Password / shared secret to use when connecting")
     bindPortPtr    :=    flag.Int("bind-port",      1337,                       "The local port to bind to")
     flag.BoolVar(&verbose_mode,"verbose",false,"Set verbose mode")
     flag.Parse()

     if(verbose_mode) {
        fmt.Println("STUN server:     ", *stunServerPtr)
        fmt.Println("Remote peer:     ", *connectAddrPtr)
        fmt.Println("Binding to port: ", *bindPortPtr)
     }

     nat_probe(*stunServerPtr)
     open_tun()

     derive_key(*passwordPtr)
}
