import json
import openpyxl
import os
from pandas import json_normalize
import csv

dir_list = next(os.walk('data/pb'))[1]

list_folders_tenants = []
for folder in dir_list:

    folder_contents = os.scandir("data/pb/" + folder)
    count = 0

    for f in folder_contents:

        if f.is_dir() and (f.name == 'egov-location' or f.name == 'ws-services-calculation'):
            count += 1

    folder_contents.close()

    if count != 0:
        list_folders_tenants.append(folder)

folders = []
folders.extend(list_folders_tenants)
print(len(folders))
billing_list = []
tenant_json_file_path = "data/pb/tenant/tenants.json"
tenant_json_file = open(tenant_json_file_path)
tenant_json_file_data = json.load(tenant_json_file)
tenant_map = {}

for tenant in tenant_json_file_data['tenants']:
    tenant_map[tenant['code']] = tenant

for folder in folders:
    if folder=='testing':
        continue
    # print('adding pb.' + folder + '....', end='\n')
    json_file = "data/pb/" + folder + "/ws-services-calculation/WCBillingSlab.json"
    file = open(json_file)
    data = json.load(file)
    df = json_normalize(data, record_path='WCBillingSlab')
    df_residential = df[
        df.buildingType == "RESIDENTIAL"]
    df_resd_flat = df_residential[df_residential.calculationAttribute == 'Flat']
    df_resd_flat_connectionType = df_resd_flat[df_resd_flat.connectionType == 'Non_Metered']
    df_commercial = df[
        df.buildingType == "COMMERCIAL"]
    df_comm_flat = df_commercial[df_commercial.calculationAttribute == 'Flat']
    df_comm_flat_connectionType = df_comm_flat[df_comm_flat.connectionType == 'Non_Metered']

    df_mixed = df[
        df.buildingType == "MIXED"]
    df_mixed_flat = df_mixed[df_mixed.calculationAttribute == 'Flat']
    df_mixed_flat_connectionType = df_mixed_flat[df_mixed_flat.connectionType == 'Non_Metered']

    df_public_sector = df[
        df.buildingType == "PUBLICSECTOR"]
    df_public_sector_flat = df_public_sector[df_public_sector.calculationAttribute == 'Flat']
    df_public_sector_flat_connectionType = df_public_sector_flat[df_public_sector_flat.connectionType == 'Non_Metered']

    req_data = {
        'tenantId': data['tenantId'],
        'villageCode': tenant_map[data['tenantId']]["city"]["code"],
        'tenantName': tenant_map[data['tenantId']]['name'],
        'RESIDENTIAL_FLAT_Non_Metered_Minimum_Charge': int(df_resd_flat_connectionType["minimumCharge"].values[0]),
        'COMMERCIAL_FLAT_Non_Metered_Minimum_Charge': int(df_comm_flat_connectionType["minimumCharge"].values[0]),
        'MIXED_FLAT_Non_Metered_Minimum_Charge': int(df_comm_flat_connectionType["minimumCharge"].values[0]),
        'PUBLICSECTOR_FLAT_Non_Metered_Minimum_Charge': int(df_comm_flat_connectionType["minimumCharge"].values[0]),
    }

    billing_list.append(req_data)

    # print("added", end='\n')
    file.close()
# Serializing json
json_object = json.dumps(billing_list, indent=4)

# Writing to sample.json
with open("water_billing_json.json", "w") as outfile:
    outfile.write(json_object)
data_file = open('water_billing_csv_pb.csv', 'w', newline='')

csv_writer = csv.writer(data_file)

count = 0
for data in billing_list:
    if count == 0:
        header = data.keys()
        csv_writer.writerow(header)
        count += 1
    csv_writer.writerow(data.values())

data_file.close()
