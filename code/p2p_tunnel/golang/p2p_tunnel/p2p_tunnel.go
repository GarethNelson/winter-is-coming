package main

import "log"
import "flag"
import "fmt"
import "github.com/GarethNelson/go-stun/stun"
import "github.com/GarethNelson/water"
import "golang.org/x/crypto/pbkdf2"
import "crypto/sha1"
import "crypto/rand"
import "crypto/aes"
import "crypto/cipher"
import "io"
import "net"
import "strconv"

var verbose_mode = false

func udp_listen(port_no int) net.PacketConn {
     listener,err := net.ListenPacket("udp",":" + strconv.Itoa(port_no))
     if err != nil {
        log.Fatal(err)
     }
     return listener
}

func nat_probe(server_addr string, bind_port int) net.PacketConn {
     conn := udp_listen(bind_port)
     if(verbose_mode) {
        fmt.Println("Probing NAT setup...")
     }
     stun_client := stun.NewClientWithConnection(conn)
     stun_client.SetServerAddr(server_addr)
     stun_client.SetVerbose(verbose_mode)
     nat_type, host, err := stun_client.Discover()

     if err != nil {
        if nat_type != stun.NATNone {
           log.Fatal(err)
        }
     }


     if(verbose_mode) {
         fmt.Println("Detected NAT type: ",nat_type)
         if nat_type != stun.NATNone {
            fmt.Println("External IP:       ",host.IP())
            fmt.Println("External port:     ",host.Port())
         }
     }
     return conn
}

func open_tun() *water.Interface {
     config      := water.Config{DeviceType: water.TUN}
     tun_if, err := water.New(config)
     if err != nil {
        log.Fatal(err)
     }
     log.Printf("Opened TUN device: %s\n", tun_if.Name())
     return tun_if
}

func derive_key(password string) []byte {
     salt := []byte{0xFE,0xED,0xFA,0xCE,0xDE,0xAD,0xBE,0xEF} // this is obviously a terrible idea and would not happen in production code
     key  := pbkdf2.Key([]byte(password), salt, 16, 32, sha1.New)
     return key
}

func encrypt_packet(packet []byte, key []byte) []byte {
     block, err := aes.NewCipher(key)
     if err != nil {
        log.Fatal(err)
     }
     retval := make([]byte, aes.BlockSize+len(packet))
     iv     := retval[:aes.BlockSize]
     if _, err := io.ReadFull(rand.Reader, iv); err != nil {
        log.Fatal(err)
     }
     stream := cipher.NewCTR(block, iv)
     stream.XORKeyStream(retval[aes.BlockSize:], packet)
     return retval

}

func main() {
     stunServerPtr  := flag.String("stun-server",    "172.16.0.10:3478",         "STUN/TURN server to use")
     connectAddrPtr := flag.String("connect-address","172.16.0.2:1337",          "Address of remote peer to attempt to connect to")
     passwordPtr    := flag.String("password",       "CorrectHorseBatteryStaple","Password / shared secret to use when connecting")
     bindPortPtr    :=    flag.Int("bind-port",      1337,                       "The local port to bind to")
     flag.BoolVar(&verbose_mode,"verbose",false,"Set verbose mode")
     flag.Parse()

     remote_addr,err := net.ResolveUDPAddr("udp", *connectAddrPtr)

     if err != nil {
        fmt.Println("Invalid remote peer address!")
        return
     }

     if(verbose_mode) {
        fmt.Println("STUN server:     ", *stunServerPtr)
        fmt.Println("Remote peer:     ", *connectAddrPtr)
        fmt.Println("Binding to port: ", *bindPortPtr)
     }

     udp_conn      := nat_probe(*stunServerPtr, *bindPortPtr).(*net.UDPConn)
     tun_device    := open_tun()
     shared_secret := derive_key(*passwordPtr)

     fmt.Println("Ready to receive packets")

     packet := make([]byte, 2000)
     for {
         n, err := tun_device.Read(packet)
         if err != nil {
            log.Fatal(err)
         }
         if verbose_mode {
            log.Printf("Read local packet: % x\n", packet[:n])
         }
         encrypted_pack := encrypt_packet(packet[:n], shared_secret)
         if verbose_mode {
            log.Printf("Encrypted packet: % x\n", encrypted_pack)
            log.Printf("Transmitting to peer...\n")
         }
         udp_conn.WriteToUDP(encrypted_pack, remote_addr)
     }
}
