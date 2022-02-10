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


# List all the volumes present
def showVolumes():  # done
    command_formation = "ozone sh volume list | grep name"
    stdin, stdout, stderr = c.exec_command(command_formation)
    time.sleep(5)
    print("Available volumes: ")
    volume_list = list(
        map(lambda x: x.split(",\n")[0].strip().strip('"'), stdout.read().
            decode().strip().split(":")[1::3]))
    print(volume_list)


# List all the buckets inside a particular volume
def showBuckets(vol):  # done
    command_formation = f"ozone sh bucket list {vol} | grep -e name"
    stdin, stdout, stderr = c.exec_command(command_formation)
    time.sleep(5)
    print(f"Available buckets inside volume = {vol}: ")
    bucket_list = list(
        map(lambda x: x.split(":")[1].strip().strip('"'), stdout.read().
            decode().strip().split(",")[:-1]))
    print(bucket_list)


# List all the keys present in the bucket
def showKeys(vol, bucket):  # done
    command_formation = f"ozone sh key list {vol}/{bucket} | grep name"
    stdin, stdout, stderr = c.exec_command(command_formation)
    time.sleep(5)
    print(f"Available keys inside bucket {bucket} of volume {vol}: ")
    key_list = list(
        map(lambda x: x.split(":")[1].strip().strip('"'), stdout.read().
            decode().strip().split(",")[:-1]))
    print(key_list)
    return key_list


# Create a new volume
def createVolume(vol):  # done
    command_formation = f"ozone sh volume create {vol}"
    execute(command_formation)


# Create a new bucket inside a volume
def createBucket(vol, bucket):  # done
    command_formation = f"ozone sh bucket create {vol}/{bucket}/"
    execute(command_formation)


# Create a new key inside a bucket
def createKey(vol, bucket, key):  # done
    command_formation = f"ozone fs -touch o3fs://{bucket}.{vol}.ozone1/{key}"
    execute(command_formation)


# Create n keys at a time inside a bucket
def createManyKeys(vol, bucket, n):  # done
    for i in range(1, n + 1):
        key_name = f"key{i}"
        createKey(vol, bucket, key_name)


# Delete a particular volume
def deleteVolume(vol):  # done
    command_formation = f"ozone sh volume delete {vol}"
    err = execute(command_formation)[2]
    return err.read().decode().strip()


# Delete a particular bucket from a volume
def deleteBucket(vol, bucket):  # done
    command_formation = f"ozone sh bucket delete {vol}/{bucket}"
    execute(command_formation)


# Delete a key from the bucket
def deleteKey(vol, bucket, key_name):  # done
    command_formation = f"ozone sh key delete {vol}/{bucket}/{key_name}"
    execute(command_formation)


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
                createVolume(volume_name)
                print("Volume created successfully!!")
                showVolumes()
            case 2:
                showVolumes()
                vol_name = input("Choose the volume: ")
                bucket_name = input("Enter the bucket name: ")
                createBucket(vol_name, bucket_name)
                print("Bucket created successfully!!")
                showBuckets(vol_name)
            case 3:
                showVolumes()
                vol_name = input("Choose the volume: ")
                showBuckets(vol_name)
                bucket_name = input("Choose the bucket: ")
                key_name = input("Enter the key name: ")
                createKey(vol_name, bucket_name, key_name)
                print("Key created successfully.")
                showKeys(vol_name, bucket_name)
            case 4:
                showVolumes()
            case 5:
                vol_name = input("Enter the volume name: ")
                showBuckets(vol_name)
            case 6:
                vol_name = input("Enter the volume name: ")
                bucket_name = input("Enter the bucket name: ")
                showKeys(vol_name, bucket_name)
            case 7:
                num = int(input("Enter the number of keys(N) you want to add"
                                "(keys will be in format key1, key2,...keyN): "))
                showVolumes()
                vol_name = input("Choose the volume: ")
                showBuckets(vol_name)
                bucket_name = input("Choose the bucket: ")
                print("Putting keys..Please wait..")
                createManyKeys(vol_name, bucket_name, num)
                print("All the keys created successfully!")
                showKeys(vol_name, bucket_name)
            case 8:
                showVolumes()
                vol_name = input("Choose the volume: ")
                showBuckets(vol_name)
                bucket_name = input("Choose the bucket: ")
                keys = showKeys(vol_name, bucket_name)
                print("Deleting all keys.. Please wait")
                deleteAllKeys(vol_name, bucket_name, keys)
                print("All keys deleted from the specified bucket")
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
                showBuckets(vol_name)
                bucket_name = input("Enter the bucket to delete: ")
                deleteBucket(vol_name, bucket_name)
                print("Bucket deleted successfully!")
                showBuckets(vol_name)
            case 11:
                showVolumes()
                vol_name = input("Choose the volume: ")
                showBuckets(vol_name)
                bucket_name = input("Choose the bucket: ")
                showKeys(vol_name, bucket_name)
                key_name = input("Enter the key name to delete: ")
                deleteKey(vol_name, bucket_name, key_name)
                print("Key deleted successfully!")
                showKeys(vol_name, bucket_name)


if __name__ == "__main__":
    main()

c.close()
print("SSH Closed!")
