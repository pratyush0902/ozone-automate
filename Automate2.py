import json
import time
import paramiko


# import re

# SSH Connection to Ozone
def sshConnect():  # done
    private_key = paramiko.RSAKey.from_private_key_file("myKeys", password="company")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("connecting...")
    client.connect(hostname="172.27.179.192", username="root", pkey=private_key, password="password")
    print("connected!!")
    return client


# Executing the exec_command
def execute(command_formation):  # done
    stdin, stdout, stderr = c.exec_command(command_formation)
    time.sleep(5)
    return stdin, stdout, stderr


# Returning the output in the format desired
def formatter(stdout):  # done
    out = stdout.read().decode().strip()
    res = json.loads(out)
    result = []
    for i in res:
        result.append(i.get('name'))
    return result


# List all the volumes present
def showVolumes():  # done
    command_formation = "ozone sh volume list /"
    stdin, stdout, stderr = c.exec_command(command_formation)
    time.sleep(5)
    print("Available volumes: ")
    vol_list = formatter(stdout)
    print(vol_list)


# List all the buckets inside a particular volume
def showBuckets(vol):  # done
    command_formation = f"ozone sh bucket list {vol}"
    stdin, stdout, stderr = c.exec_command(command_formation)
    time.sleep(5)
    error_string = stderr.read().decode().strip()
    if error_string:
        return error_string

    print(f"Available buckets inside volume = {vol}: ")
    bucket_list = formatter(stdout)
    print(bucket_list)
    return ""


# List all the keys present in the bucket
def showKeys(vol, bucket):  # done
    command_formation = f"ozone sh key list {vol}/{bucket}"
    stdin, stdout, stderr = c.exec_command(command_formation)
    time.sleep(5)
    error_string = stderr.read().decode().strip()
    if error_string:
        return [], error_string
    print(f"Available keys inside bucket {bucket} of volume {vol}: ")
    key_list = formatter(stdout)
    print(key_list)
    return key_list, ""


# Create a new volume
def createVolume(vol):  # done
    command_formation = f"ozone sh volume create {vol}"
    err = execute(command_formation)[2]
    return err.read().decode().strip()


# Create a new bucket inside a volume
def createBucket(vol, bucket):  # done
    command_formation = f"ozone sh bucket create {vol}/{bucket}/"
    err = execute(command_formation)[2]
    return err.read().decode().strip()


# Create a new key inside a bucket
def createKey(vol, bucket, key):  # done
    command_formation = f"ozone fs -touch o3fs://{bucket}.{vol}.ozone1/{key}"
    err = execute(command_formation)[2]
    return err.read().decode().strip()


# Create n keys at a time inside a bucket
def createManyKeys(vol, bucket, key_names):  # done
    for key in key_names:
        err_catch = createKey(vol, bucket, key)
        if err_catch != "":
            return err_catch
    return ""


# Delete a particular volume
def deleteVolume(vol):  # done
    command_formation = f"ozone sh volume delete {vol}"
    err = execute(command_formation)[2]
    return err.read().decode().strip()


# Delete a particular bucket from a volume
def deleteBucket(vol, bucket):  # done
    command_formation = f"ozone sh bucket delete {vol}/{bucket}"
    err = execute(command_formation)[2]
    return err.read().decode().strip()


# Delete a key from the bucket
def deleteKey(vol, bucket, key_name):  # done
    command_formation = f"ozone sh key delete {vol}/{bucket}/{key_name}"
    err = execute(command_formation)[2]
    return err.read().decode().strip()


# Delete all the keys from the bucket
def deleteAllKeys(vol, bucket, key_list):  # done
    for key in key_list:
        deleteKey(vol, bucket, key)


c = sshConnect()


def main():
    user_response = 0
    while user_response != 12:
        print("\n\nWhat do you wanna do. \n"
              "1.Create a volume.\n"
              "2.Create a bucket inside a particular volume.\n"
              "3.Create key inside a Bucket.\n"
              "4.List all volumes\n"
              "5.List all buckets inside a particular volume\n"
              "6.List all the keys inside a bucket\n"
              "7.Uploading many keys at a time(say n) into a bucket\n"
              "8.Deleting all the keys present in the bucket\n"
              "9.Delete a volume\n"
              "10.Delete a bucket from a volume\n"
              "11.Delete a key from a bucket\n"
              "12.Exit\n"
              )
        user_response = int(input("Enter your response[1-12]\n"))
        match user_response:
            case 1:
                volume_name = input("Enter the name of the volume: ")
                err = createVolume(volume_name)
                if err == "":
                    print("Volume created successfully!!")
                    showVolumes()
                else:
                    print(err)
            case 2:
                showVolumes()
                vol_name = input("Choose the volume: ")
                bucket_name = input("Enter the bucket name: ")
                err = createBucket(vol_name, bucket_name)
                if err == "":
                    print("Bucket created successfully!!")
                    showBuckets(vol_name)
                else:
                    print(err)

            case 3:
                showVolumes()
                vol_name = input("Choose the volume: ")
                err = showBuckets(vol_name)
                if err != "":
                    # print(type(err))
                    print(err)
                else:
                    bucket_name = input("Choose the bucket: ")
                    key_name = input("Enter the key name: ")
                    err = createKey(vol_name, bucket_name, key_name)
                    if err == "":
                        print("Key created successfully.")
                        showKeys(vol_name, bucket_name)
                    else:
                        # print(type(err))
                        # The error output will have warning lines as well as the actual error message
                        # Last line is the actual error message, it is in the form " touch: <error message> "
                        # so, splitlines()[-1] is for getting the last line and partition is for extracting the
                        # real error message without the "touch"
                        print(err.splitlines()[-1].partition(": ")[2])

            case 4:
                showVolumes()
            case 5:
                vol_name = input("Enter the volume name: ")
                err = showBuckets(vol_name)
                if err == "":
                    pass
                else:
                    print(err)
            case 6:
                vol_name = input("Enter the volume name: ")
                bucket_name = input("Enter the bucket name: ")
                key_list, err = showKeys(vol_name, bucket_name)
                if err == "":
                    pass
                else:
                    print(err)
            case 7:
                showVolumes()
                vol_name = input("Choose the volume: ")
                err = showBuckets(vol_name)
                if err != "":
                    # print(type(err))
                    print(err)
                else:
                    bucket_name = input("Choose the bucket: ")
                    num = int(input("Enter the number of keys(N) you want to add: "))
                    key_names = []
                    for i in range(num):
                        key_name = input(f"Enter the name of {i + 1} key: ")
                        key_names.append(key_name)

                    print("Putting keys..Please wait..")
                    err = createManyKeys(vol_name, bucket_name, key_names)
                    if err == "":
                        print("All the keys created successfully!")
                        showKeys(vol_name, bucket_name)
                    else:
                        # print(type(err))
                        # The error output will have warning lines as well as the actual error message
                        # Last line is the actual error message, it is in the form " touch: <error message> "
                        # so, splitlines()[-1] is for getting the last line and partition is for extracting the
                        # real error message without the "touch"
                        print(err.splitlines()[-1].partition(": ")[2])

            case 8:
                showVolumes()
                vol_name = input("Choose the volume: ")
                err = showBuckets(vol_name)
                if err == "":
                    bucket_name = input("Choose the bucket: ")
                    keys, err = showKeys(vol_name, bucket_name)
                    if err == "":
                        print("Deleting all keys.. Please wait")
                        deleteAllKeys(vol_name, bucket_name, keys)
                        print("All keys deleted from the specified bucket")
                    else:
                        print(err)
                else:
                    print(err)
            case 9:
                showVolumes()
                vol_name = input("Enter the Volume to delete: ")
                err = deleteVolume(vol_name)
                if err != "":
                    print(
                        "Volume cant be deleted, Please check if its empty or not. \nOnly empty volumes can be deleted.")
                else:
                    print("Volume deleted successfully!")
                    showVolumes()
            case 10:
                showVolumes()
                vol_name = input("Choose the volume: ")
                err = showBuckets(vol_name)
                if err == "":
                    bucket_name = input("Enter the bucket to delete: ")
                    err = deleteBucket(vol_name, bucket_name)
                    if err == "":
                        print("Bucket deleted successfully!")
                        showBuckets(vol_name)
                    else:
                        print(err)
                else:
                    print(err)
            case 11:
                showVolumes()
                vol_name = input("Choose the volume: ")
                err = showBuckets(vol_name)
                if err != "":
                    # print(type(err))
                    print(err)
                else:
                    bucket_name = input("Choose the bucket: ")
                    key_list, err = showKeys(vol_name, bucket_name)
                    if err == "":
                        key_name = input("Enter the key name to delete: ")
                        err = deleteKey(vol_name, bucket_name, key_name)
                        if err == "":
                            print("Key deleted successfully!")
                            showKeys(vol_name, bucket_name)
                        else:
                            print(err)
                    else:
                        print(err)


if __name__ == "__main__":
    main()

c.close()
print("SSH Closed!")
