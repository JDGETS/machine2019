import sys
sys.path.insert(0, 'src')

import config

if sys.argv[1] == 'doggo':
    import doggo
    doggo.main()

elif sys.argv[1] == 'pupper':
    import pupper
    pupper.main()

elif sys.argv[1] == 'rpyc':
    import doggo.arm.arm_service

    doggo.arm.arm_service.main()
