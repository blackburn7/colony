import sys
from typing import List
import uuid
import anthropic
import asyncio
import time
from tqdm import tqdm
from rich import print
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn



class Colony:
    
    def __init__(self):
        self.workers: dict[Worker] = {}
        self.name_to_id = {}
        self.client = anthropic.AsyncAnthropic()
        self.initial: Worker | None = None
        self.final: Worker | None = None
        self.path = {}
        
        
    def worker_status(self, name: str):
        """ get current status of worker """
        self.workers[self.name_to_id[name]].status(verbose=True)
        
    def start_worker(self, name: str):
        """ create new worker """
        
        # check worker doens't already exist
        if name in self.name_to_id:
            raise TypeError("worker with this name already exists")
        
        # get and add worker id
        worker_id = str(uuid.uuid4())
        self.name_to_id[name] = worker_id
        
        # create new worker
        new_worker = Worker(name, worker_id, self)
        
        # add new worker to colony
        self.workers[worker_id] = new_worker
        
        
        print(f"worker \"{name}\" has been successfully created")
    
    def status(self):
        console.print("colony", style="bold red underline")
        console.print(f"workers: {len(self.workers)}")
        console.print(f"initial: {self.initial.name if self.initial else None}")
        console.print(f"final: {self.final.name if self.final else None}")
        for name in self.name_to_id.keys():
            self.worker_status(name)
        
    def worker_status(self, name: str):
        
        if name not in self.name_to_id:
            raise TypeError("worker does not exist")
        
        self.workers[self.name_to_id[name]].status(verbose=False)
    
    def set_initial(self, name: str):
        """ set initial worker """

        if name not in self.name_to_id:
            raise TypeError("worker does not exist")
        
        # remove previous initial
        if self.initial:
            self.initial.is_inital = False
        
        # set new initial worker
        self.initial = self.workers[self.name_to_id[name]]
        self.initial.is_inital = True
        
        console.print(f"\"{self.initial.name}\" is now the initial worker")
        
    def set_final(self, name: str):
        """ set final worker """
        
        if name not in self.name_to_id:
            raise TypeError("worker does not exist")
        
        # remove previous final worker
        if self.final:
            self.final.is_final = False
            
        # set new final worker
        self.final = self.workers[self.name_to_id[name]]
        self.final.is_final = True
        
        console.print(f"\"{self.final.name}\" is now the final worker")
        
    async def prompt(self, prompt: str):
        if not self.initial or not self.final:
            raise TypeError("set starting and ending points of colony")
        

        # create response task
        current_worker = self.initial
        while current_worker != None:
            console.print(f"prompting {current_worker.name}...")
            current_worker.last_prompt = prompt
            response = await current_worker.prompt(prompt)
            prompt = response[0].text
            current_worker.last_response = prompt
            current_worker = current_worker.child

        print(prompt)
        return prompt
    
    def link(self, parent_name: str, child_name: str) -> None:
        """" link parent and child workers"""
        
        if parent_name not in self.name_to_id or child_name not in self.name_to_id:
            raise TypeError("child or parent does not exist")
        
        parent: Worker = self.workers[self.name_to_id[parent_name]]
        child: Worker = self.workers[self.name_to_id[child_name]]
        
        parent.child = child
        child.parent = parent
        
        console.print(f"{parent_name} {child_name} linked")
        
    def set_role(self, name: str, role: str):
        """ set role of worker """
        
        if name not in self.name_to_id:
            raise TypeError("worker does not exist")
        self.workers[self.name_to_id[name]].role = role
        
    

class Worker:
    
    def __init__(self, name: str, id: str, colony: Colony, role: str = ""):
        
        self.name = name
        self.id = id
        self.colony = colony
        self.role = role
        self.is_inital = False
        self.is_final = False
        self.parent: Worker | None = None
        self.child: Worker | None = None
        
        self.last_prompt = None
        self.last_response = None
        
        self.DEFAULT_ROLE = "you are a helpful assistant in swarm of AI agents. if I tell you to output something do it in the context that your output will be passed as the input to another agent"
        self.role = role

            
            
    def status(self, verbose):
        console.print(f"{self.name}", style="underline red")
        if self.is_inital: console.print("initial worker", style="red")
        if self.is_final: console.print("final worker", style="blue")
        console.print(f"id: {self.id}")
        console.print(f"role: {self.role}")
        console.print(f"parent: {self.parent.name if self.parent else None}")
        console.print(f"child: {self.child.name if self.child else None}")
        if verbose:
            console.print(f"last prompt: {self.last_prompt}")
            console.print(f"last response: {self.last_response}")
        
        
    async def prompt(self, prompt: str):
        
        client = self.colony.client
        
        with Progress(SpinnerColumn(), BarColumn(bar_width=40), transient=True) as progress:
            task = progress.add_task("", total=None)
            message_task = asyncio.create_task(
                client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    temperature=0,
                    system=self.DEFAULT_ROLE+self.role,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                )
            )
            
            while not message_task.done():  
                progress.update(task, advance=1)
                await asyncio.sleep(0.1)  
                    
            response = await message_task
                     
        return response.content
    
    def set_role(self, role: str) -> None:
        self.role = role


    
    
    
    
def print_commands() -> None:
    print("commands:")
    print(" - help: list commands")
    print(" - start {*name}: begin one or more workers worker")
    print(" - link {parent_worker} {child_worker}")
    print(" - status {name}: get worker status")
    print(" - colony: get colony status")
    print(" - initial {name}: initialize worker")
    print(" - final {name}: set final worker")
    print(" - prompt {prompt}: set initial worker")
    print(" - role {name} {role}: set worker role")


console = Console()

async def main():
    
    
    console.print("welcome to colony...", style="bold red")
    print_commands()

    
    colony = Colony()

    while True:
        try:
            commands = input("enter command: ").split()
            
            if not commands or commands[0].lower() == 'exit':
                break
            
            
            command = commands[0]
            
            if command == "status":
                if len(commands) != 2:
                    print("provide worker name")
                else:
                    name = commands[1]
                    colony.worker_status(name)
            elif command == "colony":
                colony.status()
            elif command == "start":
                if len(commands) < 2:
                    print("provide worker name")
                else:
                    for name in commands[1:]:
                        colony.start_worker(name)
                
            elif command == "prompt":
                if len(commands) == 1:
                    print("provide prompt")
                else:
                    prompt = " ".join(commands[1:])
                    await colony.prompt(prompt)
                
            elif command == "initial":
                if len(commands) != 2:
                    print("provide worker name")
                else:
                    initial = commands[1]
                    colony.set_initial(initial)
            elif command == "final":
                if len(commands) != 2:
                    print("provide worker name")
                else:
                    final = commands[1]
                    colony.set_final(final)
            elif command == "link":
                if len(commands) != 3:
                    print("proivde two worker names")
                else:
                    worker_1 = commands[1]
                    worker_2 = commands[2]
                    colony.link(worker_1, worker_2)
            elif command == "role":
                if len(commands) < 3:
                    print("provide worker name and updated role")
                else:
                    worker = commands[1]
                    role = " ".join(commands[2:])
                    colony.set_role(worker, role)
                
            elif command == "help":
                print_commands()
            else:
                print("not a valid command, run \'help\' to see list of commands")

            
            
            
            command = commands[0]

            
        except KeyboardInterrupt:
            print()
            sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
