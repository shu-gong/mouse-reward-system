import socket
import time

# Read i bytes from array as int
def int_read_from_array(array, array_index, i):
    var_bytes = array[array_index:array_index+i]
    var = hex(int.from_bytes(var_bytes, 'little'))
    return var, array_index + i

# Read i bytes from array as i chars
def char_read_from_array(array, array_index, i):
    var_bytes = array[array_index:array_index+i]
    # native to unicode???
    var = str(var_bytes,'utf-8')
    return var, array_index + i

# Set localhost
HOST = '127.0.0.1'

# Connect to spike server
spike_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
spike_socket.connect((HOST, 5002))

# Connect to command server
cmd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cmd_socket.connect((HOST, 5000))

# Clear TCP data output to ensure no TCP channels are enabled at
# the begining of this script

# Send TCP commands to set up TCP data output
cmd_socket.sendall(b'set a-000.TCPDataOutputEnabled true;set a-000.TCPDataOutputEnabledSpike true;set runmode run;')
print('Connection set up...')

# Wait 1 second to make sure data sockets are ready to begin
time.sleep(1)

# Each spike chunk contains 4 bytes for magic number, 5 bytes for natice
# channel name, 4 bytes for timestamp, and 1 byte for id. Total: 14 bytes
bytes_per_spike_chunk = 14

# Loop
while True:
    print('Start to receive data from stream...')

    spike_array = spike_socket.recv(1024)
    if spike_array == b'':
        raise RuntimeError("socket connection broken")

    if spike_array:
        print(spike_array)

    if len(spike_array) > 0 and len(spike_array) % bytes_per_spike_chunk == 0:
        print('Successfully received the 1st chunk')
        chunks_to_read = len(spike_array) / bytes_per_spike_chunk
        spike_index = 0

        for chunk in range(int(chunks_to_read)):

            print('Start to process the {} chunk'.format(chunk+1))

            # Make sure we get the correct magic number for this chunk
            magic_number, spike_index = int_read_from_array(spike_array, spike_index, 4)
            if magic_number != '0x3ae2710f':
                print('incorrect spike magic number', magic_number)
            if magic_number == '0x3ae2710f':
                print('magic number is right', magic_number)

            # Next 5 bytes are chars of native channel name
            native_channel_name, spike_index = char_read_from_array(spike_array, spike_index, 5)
            print(native_channel_name)

            # Next 4 bytes are int timestamp
            single_timestamp, spike_index = int_read_from_array(spike_array, spike_index, 4)
            print(int(single_timestamp,16))

            # Next 1 byte is int id
            single_ID, spike_index = int_read_from_array(spike_array, spike_index, 1)

            # Calculate the firing rate
            # TODO

            print(int(single_ID,16))


# print('Disconnected')

