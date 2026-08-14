"""
Pygbag / WebAssembly entry point for Magicor.

Desktop users should run Magicor.py instead.
Pygbag bundles pygame; do not declare pygame or pillow here (no wasm wheels).
"""
import asyncio

# Flip to True to verify the pygbag runtime without loading the full game.
WASM_BOOT_TEST = False


async def _boot_test():
    import pygame

    print("BOOT TEST: start", flush=True)
    pygame.display.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    frame = 0
    while True:
        screen.fill((20, 40, 80 + (frame % 120)))
        pygame.display.flip()
        clock.tick(30)
        frame += 1
        if frame % 60 == 0:
            print(f"BOOT TEST: frame {frame}", flush=True)
        await asyncio.sleep(0)


async def _run_game():
    print("magicor wasm: starting", flush=True)
    from magicor import GameEngine, getConfig, parse_printkeys
    from magicor.states.intro import CopyrightNoticeState

    conf = getConfig(["etc/magicor.conf"])
    conf["user_path"] = "."
    conf["data_path"] = "data"
    conf["fullscreen"] = 0
    conf["joystick"] = 0
    conf["music"] = 1
    conf["sound"] = 1
    parse_printkeys("")
    gameEngine = GameEngine(conf)
    print("magicor wasm: engine ready", flush=True)
    await gameEngine.start(
        CopyrightNoticeState(conf, None, gameEngine.screen)
    )


async def main():
    if WASM_BOOT_TEST:
        await _boot_test()
    else:
        await _run_game()


print("main.py: module loaded", flush=True)
asyncio.run(main())
