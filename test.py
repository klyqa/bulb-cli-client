#!/usr/bin/env python3

import asyncio
from dataclasses import dataclass
from typing import Callable
import random

import datetime 
import logging
import functools, traceback


async def f():
    send_event_cb: asyncio.Event = asyncio.Event()
    async def d():
        await asyncio.sleep(2)
        send_event_cb.set()
    asyncio.create_task(d())
    await send_event_cb.wait()
    await send_event_cb.wait()


asyncio.run(f())

class OK():
    ok = "ok"
    def __init__(self):
        self.ok = "ok2"

    def a(self):
        async def b():
            print(self.ok)
        b()
    
ff = OK()
ff.a()

async def test3():
    while True:
        print("ok")
        await asyncio.sleep(1)

async def test2():
    try:
        t3 = asyncio.create_task(test3())
        await asyncio.sleep(10)
    except:
        pass
        print("t2 ended")

async def test():
    t2 = asyncio.create_task(test2())
    await asyncio.wait_for(t2, timeout=1.0)
    print("t2 wait ended")
    await asyncio.sleep(4)

asyncio.run(test())

#@dataclass
class O:
    i: str

    def __init__(self):
        self.i = ""
        
    def __str__(self) -> str:
        s = f"O Object\n"
        s = s +  f"i: {self.i}"
        return s


    def __repr__(self) -> str:
    # def __repr__(self):
        s = f"O Object"
        s = s +  f"i: {self.i}"
        return s

a: O = O()
a.i="ok"

def pass_by_ref(a2: list[O]):
    b = O()
    b.i="ok2"
    a2[0] = b

print(a)
pass_by_ref([a])
print(a)

from singleton_decorator import singleton

class A:
    a: str

a = A()
a.a = "Ok"

@singleton
class Test:

    test: str 

    def __init__(self):
        print("Ok")
        self.test = "okkk"
test = Test()
test.test = "okkkk3"
test = Test()

@singleton
class Tcp_udp_port_lock:

    lock: AsyncIOLock 

    def __init__(self):
        print("Ok")
        self.lock = AsyncIOLock() 

from enum import Enum

LOGGER = logging.getLogger(__package__)
LOGGER.setLevel(level=logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(levelname)-8s - %(message)s")

logging_hdl = logging.StreamHandler()
logging_hdl.setLevel(level=logging.DEBUG)
logging_hdl.setFormatter(formatter)

LOGGER.addHandler(logging_hdl)

class Bulb_tcp_task_supervisor():
    started: datetime.datetime
    task: asyncio.Task

    def __init__(self, task, started):
        self.task = task
        self.started = started
    

__send_loop_sleep: asyncio.Task = None
tasks_done: list[asyncio.Task] = []
tasks_undone: list[asyncio.Task] = []
# tasks_done[0].exception()

# message_queue: list[tuple] = []
message_queue: dict[tuple] = {}
message_queue_new: list[tuple] = []

d: Callable[[None], None] = None

def de():
    return asyncio.current_task()._repr_info()


async def sleep_now(a):
  
    try:
        await asyncio.sleep(a)
  
    except asyncio.CancelledError as e:
        LOGGER.debug("task cancelled.")
  
    except Exception as e:
        LOGGER.debug(e)
        pass
  
    pass

Bulb_TCP_return = Enum("Bulb_TCP_return", "sent answered wrong_uid wrong_aes tcp_error unknown_error timeout nothing_done")

Message_state = Enum("Message_state", "sent answered unsent")

class Message():
    started: datetime.datetime
    state: Message_state
    finished: datetime.datetime
    msg: str
    answer: str

    def __init__(self, started, msg, state = Message_state.unsent, finished = None, answer = ""):
        self.started = started
        self.msg = msg
        self.state = state
        self.finished = finished
        self.answer = answer


class Bulb():
    uid: int
    recv_msg_unproc: list[Message]

    def __init__(self, uid):
        self.uid = uid
        self.recv_msg_unproc = []

    def process_msgs(self):
        for msg in self.recv_msg_unproc:
            print(f"updating bulb {self.uid} entity with msg: {msg.msg}")
            self.recv_msg_unproc.remove(msg)


bulbs: dict[int, Bulb] = {}

for i in range(1,4):
    bulbs[str(i)] = Bulb(i)

async def bulb_tcp(bulb_test_id: str = str(random.randint(1,3))):
  
    bulb: Bulb = None
    return_val = Bulb_TCP_return.nothing_done

    try:
        global __send_loop_sleep, message_queue
  
        wait2 = random.uniform(0.06,0.14)
        if random.uniform(0.3,1) < 0.5:
            wait2 = 11.0
  
        LOGGER.debug(f"ok1 {wait2}")
        await asyncio.sleep(wait2)
  
        
        LOGGER.debug(f"bulb tcp proc uid {bulb_test_id}")

        bulb = bulbs[bulb_test_id] if bulb_test_id in bulbs else None

        if not "all" in message_queue:
            if not bulb_test_id in message_queue:
                LOGGER.debug(f"wrong bulb uid {bulb_test_id}")
                return Bulb_TCP_return.wrong_uid

            if not message_queue[bulb_test_id]:
                del message_queue[bulb_test_id]
                return Bulb_TCP_return.no_message_to_send

        async def send(msg):
            LOGGER.info(f"Sent msg '{msg.msg}' to bulb '{bulb_test_id}'.")
            msg.state = Message_state.sent
            message_queue[bulb_test_id].remove(msg)
            if not message_queue[bulb_test_id]:
                del message_queue[bulb_test_id]
            return_val = Bulb_TCP_return.sent

        async def recv(msg):
            if random.randint(2,9) < 8:
                msg.answer = f"test answer {random.randint(1,3)}"
                bulb.recv_msg_unproc.append(msg)
                bulb.process_msgs()
                msg.state = Message_state.answered
                return_val = Bulb_TCP_return.answered
                LOGGER.debug(f"bulb {bulb_test_id} answered msg {msg.msg}") 
                if not bulb_test_id in message_queue or not message_queue[bulb_test_id]:
                    try:
                        LOGGER.debug(f"no more messages to sent for bulb {bulb_test_id}, close tcp tunnel.")
                        # bulb_known.local.connection.shutdown(socket.SHUT_RDWR)
                        # bulb_known.local.connection.close()
                    except Exception as e:
                        pass

        i = 0
        try:
            while i < len(message_queue[bulb_test_id]):
                msg = message_queue[bulb_test_id][i]
                i = i + 1
                if msg.state == Message_state.unsent:
                    await send(msg)
                    await recv(msg)
        except:
            pass
                

        LOGGER.debug(f"ok bulb tcp proced {bulb_test_id} {msg.msg} ") #{asyncio.current_task()}
  
        try:
            __send_loop_sleep.cancel()
  
        except Exception as e:
            LOGGER.debug(e)
            pass
        return return_val
  
    except asyncio.CancelledError as e:
        LOGGER.debug(f"task bulb uid {bulb_test_id} cancelled.")
        return Bulb_TCP_return.timeout
  
    except Exception as e:
        LOGGER.debug(e)
        pass
        return Bulb_TCP_return.unknown_error
  
    return (return_val, bulb)

send_loop_max_sleep_time = 0.3

async def send_command_loop(timeout=2.0):

    LOGGER.debug("new command send loop")
    global __send_loop_sleep, tasks_undone, tasks_done

    loop = asyncio.get_event_loop()
    loop = asyncio.get_running_loop()

    while True:

        while message_queue_new:
            """add start timestamp to new messages"""
            send_msg, target_bulb_uid, extra = message_queue_new.pop(0)
            # message_queue[target_bulb_uid].append(Message(datetime.datetime.now)(), send_msg)
            # message_queue.append((datetime.datetime.now(),) + (message_queue_new.pop(0)))
            LOGGER.debug(f"new message target {target_bulb_uid} {send_msg}")
            
            message_queue.setdefault(target_bulb_uid, []).append(Message(datetime.datetime.now(), send_msg))

        if len(message_queue) > 0:
            LOGGER.debug("broadcast")

            if random.randint(2,9) < 7:

                for i in range(1,4):
                    i = str(i)

                    if random.uniform(0.3,1) < 0.5:
                        """fake bulb i not answering current broadcast"""
                        continue

                    LOGGER.debug(f"create timeout task for the bulb {i} tcp task")
                    bulb_tcp_example_task = asyncio.create_task(bulb_tcp(i))

                    asyncio.create_task(asyncio.wait_for(bulb_tcp_example_task, timeout=timeout))
                    
                    tasks_undone.append((bulb_tcp_example_task, datetime.datetime.now()))
        
        try:
            __send_loop_sleep = asyncio.create_task(asyncio.sleep(send_loop_max_sleep_time if len(message_queue) > 0 else 1000000000))
            LOGGER.debug("send loop sleep")
            done, pending = await asyncio.wait([__send_loop_sleep])

            tasks_undone_new = []

            for task, started in tasks_undone:

                if task.done():                
                    tasks_done.append((task, started, datetime.datetime.now()))
                    e = task.exception()

                    """stop tcp channel if no more messages for the bulb in the message queue"""
                    if isinstance(task.result(), tuple):
                        ret, bulb = task.result()
                        print(f"bulb {bulb.uid} done with ret: {ret}")             
                    if e:
                        LOGGER.debug(f"Exception error in {task._coro}: {e}")
                else:
                    if datetime.datetime.now() - started > datetime.timedelta(milliseconds=int(timeout*1000)):
                        task.cancel()
                    tasks_undone_new.append((task, started))
            
            tasks_undone = tasks_undone_new

        except asyncio.CancelledError as e:
            LOGGER.error(f"sleep cancelled.")

        except Exception as e:
            LOGGER.debug(f"{e}")
            pass

        pass
    return "ok done"

def send_message(send_msg, target_bulb_uid, extra):
    global message_queue_new
   
    message_queue_new.append((send_msg, target_bulb_uid, extra))
    __send_loop_sleep.cancel()

async def random_send_messages():
   
    try:
   
        while True:
            bulb_test_id = functools.partial(random.randint,1,3)
            a = functools.partial(random.randint, 0, 256)

            send_message(f"sendmsg color: {a()} {a()} {a()}", f"{bulb_test_id()}","1")

            send_message(f"sendmsg temp: {random.randint(2000,6001)}", f"{bulb_test_id()}","1")
            if random.uniform(0.3,1) < 0.7:
                send_message(f"sendmsg brightness: {random.randint(0,101)}", f"{bulb_test_id()}","1")
            if random.uniform(0.3,1) < 0.7:
                send_message(f"sendmsg brightness: {random.randint(0,101)}", f"{bulb_test_id()}","1")
            if random.uniform(0.3,1) < 0.7:
                send_message(f"sendmsg brightness: {random.randint(0,101)}", f"{bulb_test_id()}","1")
            if random.uniform(0.3,1) < 0.7:
                send_message(f"sendmsg brightness: {random.randint(0,101)}", f"{bulb_test_id()}","1")
            if random.uniform(0.3,1) < 0.7:
                send_message(f"sendmsg brightness: {random.randint(0,101)}", f"{bulb_test_id()}","1")

            await asyncio.sleep(random.uniform(0.0,10))
   
    except Exception as e:
        LOGGER.debug(f"{e}")

send_command_loop_task: asyncio.Task = None

async def main():
    global d, send_command_loop_task
   
    d = asyncio.current_task()._repr_info
   
    while True:
   
        try:
            send_command_loop_task = asyncio.create_task(send_command_loop(timeout=2))
            asyncio.create_task(random_send_messages())
            
            done, pending = await asyncio.wait([send_command_loop_task])
            e = send_command_loop_task.exception()
            if e:
                LOGGER.debug(e)
   
        except Exception as e:
            LOGGER.debug(e)
            pass
   
        pass

asyncio.run(main())
LOGGER.debug("they done.")