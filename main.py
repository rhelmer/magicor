import asyncio
from magicor import GameEngine, getConfig, parse_printkeys
from magicor.states.intro import CopyrightNoticeState

# Do init here and load any assets right now to avoid lag at runtime or network errors.

async def main():
    print('main called')

    # Do your rendering here, note that it's NOT an infinite loop,
    # and it is fired only when VSYNC occurs
    # Usually 1/60 or more times per seconds on desktop, maybe less on some mobile devices

    conf = getConfig(['etc/magicor.conf'])
    print(conf)
    gameEngine = GameEngine(conf)
    await gameEngine.start(CopyrightNoticeState(conf, None, gameEngine.screen))

# This is the program entry point:
asyncio.run(main())

# Do not add anything from here
# asyncio.run is non-blocking on pygame-wasm