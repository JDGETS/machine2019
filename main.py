import sys
sys.path.insert(0, 'src')

import config

if sys.argv[1] == 'doggo':
    import doggo
    doggo.main()

elif sys.argv[1] == 'pupperblack':
    import pupper
    pupper.main(sys.argv[1])

elif sys.argv[1] == 'pupperred':
    import pupper
    pupper.main(sys.argv[1])

elif sys.argv[1] == 'rpyc':
    import doggo.arm.arm_service

    doggo.arm.arm_service.main()

elif sys.argv[1] == 'killswitch':
    import utils.killswitch

    utils.killswitch.main()
