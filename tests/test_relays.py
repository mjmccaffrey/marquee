
import lightset_misc
import relays

def test_relays_to_devices_1():
    module = relays.NumatoRL160001('')
    client = module.create_client(
        {i: i for i in range(module.relay_count)}
    )
    print(client)
    sixteen = '0123456789ABCDEF'
    assert module._relays_to_devices(
        client,
        relays.RelayPattern(sixteen),
    ) == ''.join(reversed(sixteen))

def test_devices_to_relays_1():
    pass

def test_set_state_of_devices():
    module = relays.NumatoRL160001('')
    client = module.create_client(
        {i: i for i in range(module.relay_count)}
    )
    sixteen = '0123456789ABCDEF'
    class sp: pass
    module._serial_port = sp # type: ignore
    # module._serial_port.read = lambda _: relays.RelayPattern(sixteen) # type: ignore
    module._set_relays = lambda rh: print(rh) # type: ignore
    assert module.set_state_of_devices(
        client,
        relays.DevicePattern('1111111100000000')
    ) is None
    print(module.relay_pattern)

