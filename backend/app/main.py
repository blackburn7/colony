import sys
from typing import List
import uuid




class Colony:
    
    def __init__(self):
        self.workers: dict[Worker] = {}
        self.name_to_id = {}
        self.id_to_name = {}
        
        
    def state(self, name: str):
        self.workers[self.name_to_id[name]].status()
        
    def start_worker(self, name: str):
        if name in self.name_to_id:
            raise TypeError("worker with this name already exists")
        worker_id = str(uuid.uuid4())
        self.name_to_id[name] = worker_id
        
    

class Worker:

    
    


def main():
    
    print("welcome to colony...")
    print("commands:")
    print(" - help: list commands")
    print(" - start {name}: begin worker")
    print(" - link {worker1} {worker2}")
    print(" - status {name}")
    print(" - assistant {messanger}")
    print(" - messanger {name}")
    
    while True:
        try:
            commands = input("enter command: ").split()
            
            if not commands or commands[0].lower() == 'exit':
                break
            
            colony = Colony()
            
            command = commands[0]
            
            if command == "state":
                colony.state()
            elif command == "start":
                colony.start_worker()
            
            
            
            
            command = commands[0]
            print(command)
            
        except KeyboardInterrupt:
            print()
            sys.exit(0)


if __name__ == '__main__':
    main()