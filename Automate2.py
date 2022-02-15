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


# Info Formatter
def infoFormatter(name, request_for, command_formation):  # done
    stdin, stdout, stderr = c.exec_command(command_formation)
    time.sleep(5)
    error_string = stderr.read().decode().strip()
    if error_string:
        return error_string
    print(f"{name} {request_for} information:  ")
    out = stdout.read().decode().strip()
    request_info = json.loads(out)
    print(request_info)
    return ""


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
def createBucket(vol, bucket, layout):  # done
    command_formation = f"ozone sh bucket create {layout} {vol}/{bucket}/"
    err = execute(command_formation)[2]
    return err.read().decode().strip()


# Create a new key inside a bucket
def createKey(vol, bucket, key, file_name):  # done
    command_formation = f"ozone sh key put {vol}/{bucket}/{key} /tmp/{file_name}"
    err = execute(command_formation)[2]
    return err.read().decode().strip()


# Create n keys at a time inside a bucket
def createManyKeys(vol, bucket, key_names, default_copy_file):  # done
    for key in key_names:
        err_catch = createKey(vol, bucket, key, default_copy_file)
        print(f"Key {key} done....")
        if err_catch != "" and "WARN" not in err_catch:
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


# Get information about a particular volume
def volumeInfo(vol_name):  # done
    command_formation = f"ozone sh volume info {vol_name}"
    err_string = infoFormatter(vol_name, "volume", command_formation)
    return err_string


# Get information about a particular bucket
def bucketInfo(vol_name, bucket_name):  # done
    command_formation = f"ozone sh bucket info {vol_name}/{bucket_name}"
    err_string = infoFormatter(bucket_name, "bucket", command_formation)
    return err_string


# Get information about a particular key
def keyInfo(vol_name, bucket_name, key_name):  # done
    command_formation = f"ozone sh key info {vol_name}/{bucket_name}/{key_name}"
    err_string = infoFormatter(key_name, "key", command_formation)
    return err_string


# Creating/Overwriting a file inside /tmp/
def createFile(file_name, content):  # done
    command_formation = f"echo '{content}' >> /tmp/{file_name}"
    err = c.exec_command(command_formation)[2]
    return err.read().decode().strip()


# Listing files inside the /tmp/ directory Note: can be scaled to any directory, taking/tmp/ for my ref
def listFiles():
    command_formation = "find /tmp/ -maxdepth 1 -type f"
    stdin, stdout, stderr = c.exec_command(command_formation)
    time.sleep(5)
    out = stdout.read().decode().strip()
    file_list = out.split("\n")
    print("Files inside /tmp/ are: ")
    print(out)
    return file_list


c = sshConnect()


def main():
    user_response = 0
    while user_response != 17:
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
              "12.Info about a volume\n"
              "13.Info about a bucket inside a volume\n"
              "14.Info about a key inside a bucket\n"
              "15.Create a file inside /tmp/\n"
              "16.List files under /tmp/ directory\n"
              "17.Exit\n"
              )
        user_response = int(input("Enter your response[1-17]\n"))
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
                is_obs = input(
                    "Do you want bucket layout to be FILE_SYSTEM_OPTIMIZED or OBJECT_STORE?\nSay FSO or OBS?: ")
                if is_obs == "FSO" or is_obs == "OBS":
                    if is_obs == "FSO":
                        layout = "-l FILE_SYSTEM_OPTIMIZED"
                    else:
                        layout = "-l OBJECT_STORE"
                    err = createBucket(vol_name, bucket_name, layout)
                    if err == "" or "Creating Bucket" in err:
                        print("Bucket created successfully!!")
                        showBuckets(vol_name)
                    else:
                        # print("Error: ")
                        print(err)
                else:
                    print("Wrong input!")
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
                    print("\nAvailable files to copy: ")
                    listFiles()  # can return a list of all the files also
                    create_new = input("Enter yes if you want to create a new file, \nand No if you want to chose "
                                       "from above list.")
                    if create_new == "No" or create_new == "Yes":
                        if create_new == "No":
                            file_name = input("Chose the file name from above: ")
                        else:
                            file_name = input("Enter the file name: ")
                            content = input("Enter the content to insert into the file: ")
                            createFile(file_name, content)
                        err = createKey(vol_name, bucket_name, key_name, file_name)
                        if err == "" or "WARN" in err:
                            print("Key created successfully.")
                            showKeys(vol_name, bucket_name)
                        else:
                            # print(type(err))
                            # NOT APPLICABLE NOW, MOVED FROM ozone fs to ozone sh
                            # The error output will have warning lines as well as the actual error message
                            # Last line is the actual error message, it is in the form " touch: <error message> "
                            # so, splitlines()[-1] is for getting the last line and partition is for extracting the
                            # real error message without the "touch"
                            print(err)
                            # print(err.splitlines()[-1].partition(": ")[2])
                    else:
                        print("Bad choice!")
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
                    print("Keys to put: ", key_names)
                    print("Putting keys..Please wait..")
                    # Default file for now that is getting copied from temp: userdata-file.sh
                    err = createManyKeys(vol_name, bucket_name, key_names, "userdata-file.sh")
                    if err == "":
                        print("All the keys created successfully!")
                        showKeys(vol_name, bucket_name)
                    else:
                        # print(type(err))
                        # NOT APPLICABLE NOW, MOVED FROM ozone fs to ozone sh
                        # The error output will have warning lines as well as the actual error message
                        # Last line is the actual error message, it is in the form " touch: <error message> "
                        # so, splitlines()[-1] is for getting the last line and partition is for extracting the
                        # real error message without the "touch"
                        print(err)
                        # print(err.splitlines()[-1].partition(": ")[2])

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
            case 12:
                vol_name = input("Enter the volume name: ")
                err = volumeInfo(vol_name)
                if err == "":
                    pass
                else:
                    print(err)
            case 13:
                vol_name = input("Enter the volume name: ")
                bucket_name = input("Enter the bucket name: ")
                err = bucketInfo(vol_name, bucket_name)
                if err == "":
                    pass
                else:
                    print(err)
            case 14:
                vol_name = input("Enter the volume name: ")
                bucket_name = input("Enter the bucket name: ")
                key_name = input("Enter the key name: ")
                err = keyInfo(vol_name, bucket_name, key_name)
                if err == "":
                    pass
                else:
                    print(err)
            case 15:
                file_name = input("Enter the file name: ")
                content = input("Enter the content to insert into the file: ")
                err = createFile(file_name, content)
                if err == "":
                    print("File created successfully!")
                    listFiles()
                else:
                    print(err)
            case 16:
                listFiles()


if __name__ == "__main__":
    main()

c.close()
print("SSH Closed!")
