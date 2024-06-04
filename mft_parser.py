import subprocess
import os,datetime
import pytsk3

def timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def get_connected_disks():
    try:
        output = subprocess.check_output(["wmic", "diskdrive", "list", "brief"], universal_newlines=True)
        disk_lines = output.splitlines()
        connected_disks = [line.split()[0] for line in disk_lines if "Disk" in line]
        return connected_disks
    except subprocess.CalledProcessError:
        raise RuntimeError("Error retrieving connected disks using WMIC.")

def choose_disk_or_image():
    while True:
        choice = input("Choose disk or image (image/disk): ").lower()
        if choice == "image":
            image_path = input("Enter image path: ")
            if os.path.isfile(image_path):
                return image_path
            else:
                print(f"Invalid image path: {image_path}")
        elif choice == "disk":
            connected_disks = get_connected_disks()
            if connected_disks:
                print("Available disks:")
                for i, disk in enumerate(connected_disks):
                    print(f"{i+1}. {disk}")
                disk_choice = int(input("Select disk number (or 0 to cancel): "))
                if 0 <= disk_choice < len(connected_disks):
                    return f"\\.\\{connected_disks[disk_choice-1]}"
                else:
                    print("Invalid disk number.")
            else:
                print("No connected disks found. Please try again.")
        else:
            print("Invalid choice. Please enter 'image' or 'disk'.")

def open_image_or_disk(path):
    try:
        return pytsk3.Img_Info(path)
    except OSError as e:
        raise OSError(f"Error opening image/disk: {path}") from e

def list_partitions(img_info):
    try:
        partition_table = pytsk3.Volume_Info(img_info)
        partitions = []
        print("Available partitions:")
        for i, partition in enumerate(partition_table):
            partition_info = {
                "desc": partition.desc.decode('utf-8') if partition.desc else "N/A",
                "start": partition.start,
                "length": partition.len
            }
            partitions.append(partition_info)
            print(f"{i+1}. Description: {partition_info['desc']}, Start: {partition_info['start']}, Length: {partition_info['length']}")
        return partitions
    except OSError as e:
        print(f"Error listing partitions: {str(e)}")

def choose_partition(partitions):
    while True:
        partition_choice = input("Choose partition number (or 'exit' to cancel): ")
        if partition_choice.lower() == "exit":
            return None
        try:
            partition_choice = int(partition_choice)
            if 0 < partition_choice <= len(partitions):
                return partitions[partition_choice - 1]
            else:
                print("Invalid partition number.")
        except ValueError:
            print("Invalid input. Please enter a valid partition number or 'exit'.")

def navigate_mft(img_info, partition):
    try:
        fs_info = pytsk3.FS_Info(img_info, offset=partition['start'] * 512)
        root_dir = fs_info.open_dir(path="/")

        mft_file = None
        for entry in root_dir:
            if entry.info.name.name.decode('utf-8') == "$MFT":
                mft_file = fs_info.open_meta(inode=entry.info.meta.addr)
                break

        if mft_file is None:
            print("Error: $MFT file not found.")
            return

        for entry in root_dir:
            if entry.info.name.name in [b'.', b'..']:
                continue

            file_name = entry.info.name.name.decode('utf-8')
            file_type = os.path.splitext(file_name)[1]
            file_size = entry.info.meta.size if entry.info.meta else "N/A"

            try:
                try:
                    creation_time = entry.info.meta.crtime
                except AttributeError:
                    creation_time = "N/A"
                modification_time = entry.info.meta.mtime
                access_time = entry.info.meta.atime
                permissions = entry.info.meta.mode
                physical_location = entry.info.meta.addr
                
                print("File Information:")
                print(f"File Name: {file_name}")
                print(f"File Type: {file_type}")
                print(f"File Size: {file_size} bytes")
                print("Creation Time:", timestamp_to_datetime(creation_time))
                print("Modification Time:", timestamp_to_datetime(modification_time))
                print("Access Time:", timestamp_to_datetime(access_time))
                print(f"Permissions: {permissions}")
                print(f"Physical Location: {physical_location}")
                print("------")
                
            except AttributeError as e:
                print(f"Error getting metadata for {file_name}: {e}")

    except OSError as e:
        print(f"Error navigating MFT: {str(e)}")

if __name__ == "__main__":
    print("**NTFS MFT Analyzer**")

    while True:
        disk_or_image_path = choose_disk_or_image()
        if not disk_or_image_path:
            break

        try:
            img_info = open_image_or_disk(disk_or_image_path)
            partitions = list_partitions(img_info)
            if partitions:
                partition = choose_partition(partitions)
                if partition:
                    navigate_mft(img_info, partition)
                else:
                    print("Exiting partition selection.")
            else:
                print("No partitions found.")
        except OSError as e:
            print(f"Error analyzing disk/image: {str(e)}")

    print("Exiting...")
