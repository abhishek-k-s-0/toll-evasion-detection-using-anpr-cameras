from web3 import Web3
hex_data = "0x546f6c6c5f56696f6c6174696f6e3a48523235433036383639" 

w3 = Web3()
readable_plate = w3.to_text(hexstr=hex_data)

print(f"Decoded Plate: {readable_plate}")