"""
class MydelionApp():
    def __init__(self, config_file=None):
        cm = ConfigurationManager(config_file)
        #print("server info", cm.server_info.mdns_group)
        print("cm.server", cm.server)
        print("sync info", cm.server_time)
        cm.server_time = 2
        
        
if __name__ == "__main__":
    
    print("Starting application")
    app = MydelionApp()
"""    