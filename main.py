import sys
sys.path.insert(0, 'src')

import config

if sys.argv[1] == 'doggo':
    import doggo
    doggo.main()

elif sys.argv[1] == 'pupper1':
    import pupper
    pupper.main(sys.argv[1])

elif sys.argv[1] == 'pupper2':
    import pupper
    pupper.main(sys.argv[1])

elif sys.argv[1] == 'rpyc':
    import doggo.arm.arm_service

    doggo.arm.arm_service.main()
