
import logging,socket,sys,os
from zeroconf import mdns, dns


def main(ip=None):
    
    print("Multicast DNS Service Discovery for Python, version", mdns.__version__)
    
    r = mdns.Zeroconf(ip or '')
    host_ip = socket.gethostbyname( socket.gethostname() )
    print("HOST IP", host_ip)
    try:
        print("1. Testing registration of a service...")
        _desc = {
                'version':'0.10',
                'a':'test value', 
                'b':'another value'
        }
        
        desc = {}
        info = mdns.ServiceInfo(
            "_http._tcp.local.", 
            "vojds_service@_http._tcp.local.",
            socket.inet_aton(host_ip), 
            1234, 
            0, 
            0, 
            desc
        )
        
        print("   Registering service...")
        print("info.address", info.address)
        try:
            r.registerService(info)
            input("mdns ... press <enter> to stop")
            """
            print("   Registration done.")
            print("2. Testing query of service information...")
            print("   Getting ZOE service:", str(r.getServiceInfo("_http._tcp.local.", "ZOE._http._tcp.local.")))
            print("   Query done.")
            print("3. Testing query of own service...")
            my_service = r.getServiceInfo("_http._tcp.local.", " >> My Service Name._http._tcp.local.")
            print("   Getting self:", str(my_service))
            print("   Query done.")
            print("4. Testing unregister of service information...")
            r.unregisterService(info)
            print("   Unregister done.")
            """
            r.unregisterService(info)
        finally:
            pass
        
        
    finally:
        r.close()

if __name__ == '__main__':
    logging.basicConfig( level = logging.DEBUG )
    usage = 'testmdnssd.py [ip.address]'
    sys.exit( main(*sys.argv[1:]) )
