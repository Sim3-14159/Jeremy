import uasyncio as asyncio
import usys as sys
import ujson

        
def read_until_null():
    """returns block of code from main computer, which ends with null (\x00)"""
    message = bytearray()
    while True:
        char = sys.stdin.buffer.read(1)
        if char == b'\x00' or not char:
            break
        message.extend(char)
    return message.decode('utf-8')


def reload_module(modulename):
    if modulename in sys.modules:
        del sys.modules[modulename]
    
    __import__(modulename)


def run(code):
    """Wraps code into an async function and compiles it as a full script
    to bypass MicroPython's strict single-statement SyntaxError.
    """
    f = open("temp_code.py", "w")
    
    module_code_text_file = open("module_code.py")
    module_code_text = module_code_text_file.read()
    module_code_text_file.close()
    
    f.write(module_code_text)
    f.write(code)
    f.close()
    reload_module("temp_code") # re-execute the temp_code.py file


async def main():
    while True:
        command = read_until_null()
        print(command)
        if not command:
            await asyncio.sleep_ms(50)
            continue
            
        try:
            run(command)
        
        except Exception as e:
            error_data = {"type": type(e).__name__, "message": str(e)}
            raw_payload = ujson.dumps(error_data).encode('utf-8')
            sys.stdout.buffer.write(b'\x02')   # ASCII start of text (SOT) marker
            sys.stdout.buffer.write(raw_payload)
            sys.stdout.buffer.write(b'\x00')  # ASCII EOF/end of text/terminator (NUL) marker
            raise e


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

