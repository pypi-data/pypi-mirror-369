from light_util import get_time
import time
import asyncio

if __name__ == "__main__":
    @get_time
    async def async_example_function(n):
        time.sleep(2)  # Simulate a delay
        # raise ValueError("An example error")
        return 1
    
    @get_time
    def example_function(n):
        time.sleep(2)  # Simulate a delay
        # raise ValueError("An example error") 
        return 1
    
    import asyncio
    asyncio.run(async_example_function(1000000))    
    example_function(1000000)