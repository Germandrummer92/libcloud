# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Outscale SDK
"""

import json
import requests
from datetime import datetime

from libcloud.compute.base import NodeDriver
from libcloud.compute.types import Provider
from libcloud.common.osc import OSCRequestSignerAlgorithmV4
from libcloud.common.base import ConnectionUserAndKey
from libcloud.compute.base import \
    Node,\
    NodeImage, \
    KeyPair, \
    StorageVolume, \
    VolumeSnapshot, \
    NodeLocation
from libcloud.compute.types import NodeState


class OutscaleNodeDriver(NodeDriver):
    """
    Outscale SDK node driver
    """

    type = Provider.OUTSCALE
    name = 'Outscale API'
    website = 'http://www.outscale.com'

    def __init__(self,
                 key: str = None,
                 secret: str = None,
                 region: str = 'eu-west-2',
                 service: str = 'api',
                 version: str = 'latest',
                 base_uri: str = 'outscale.com'
                 ):
        self.key = key
        self.secret = secret
        self.region = region
        self.connection = ConnectionUserAndKey(self.key, self.secret)
        self.connection.region_name = region
        self.connection.service_name = service
        self.service_name = service
        self.base_uri = base_uri
        self.version = version
        self.signer = OSCRequestSignerAlgorithmV4(
            access_key=self.key,
            access_secret=self.secret,
            version=self.version,
            connection=self.connection
        )
        self.NODE_STATE = {
            'pending': NodeState.PENDING,
            'running': NodeState.RUNNING,
            'shutting-down': NodeState.UNKNOWN,
            'terminated': NodeState.TERMINATED,
            'stopped': NodeState.STOPPED
        }

    def list_locations(self, ex_dry_run: bool = False):
        """
        Lists available locations details.

        :param      ex_dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       ex_dry_run: ``bool``
        :return: locations details
        :rtype: ``dict``
        """
        action = "ReadLocations"
        data = json.dumps({"DryRun": ex_dry_run})
        response = self._call_api(action, data)
        return self._to_locations(response.json()["Locations"])

    def ex_list_regions(self, ex_dry_run: bool = False):
        """
        Lists available regions details.

        :param      ex_dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       ex_dry_run: ``bool``
        :return: regions details
        :rtype: ``dict``
        """
        action = "ReadRegions"
        data = json.dumps({"DryRun": ex_dry_run})
        response = self._call_api(action, data)
        return response.json()["Regions"]

    def ex_list_subregions(self, ex_dry_run: bool = False):
        """
        Lists available subregions details.

        :param      ex_dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       ex_dry_run: ``bool``
        :return: subregions details
        :rtype: ``dict``
        """
        action = "ReadSubregions"
        data = json.dumps({"DryRun": ex_dry_run})
        response = self._call_api(action, data)
        return response.json()["Subregions"]

    def ex_create_public_ip(self, dry_run: bool = False):
        """
        Create a new public ip.

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: the created public ip
        :rtype: ``dict``
            """
        action = "CreatePublicIp"
        data = json.dumps({"DryRun": dry_run})
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def ex_delete_public_ip(self,
                            dry_run: bool = False,
                            public_ip: str = None,
                            public_ip_id: str = None):
        """
        Delete public ip.

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :param      public_ip: The EIP. In the public Cloud, this parameter is
        required.
        :type       public_ip: ``str``

        :param      public_ip_id: The ID representing the association of the
        EIP with the VM or the NIC. In a Net,
        this parameter is required.
        :type       public_ip_id: ``str``

        :return: request
        :rtype: ``dict``
        """
        action = "DeletePublicIp"
        data = {"DryRun": dry_run}
        if public_ip is not None:
            data.update({"PublicIp": public_ip})
        if public_ip_id is not None:
            data.update({"PublicIpId": public_ip_id})
        data = json.dumps(data)
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def ex_list_public_ips(self, data: str = "{}"):
        """
        List all public IPs.

        :param      data: json stringify following the outscale api
        documentation for filter
        :type       data: ``string``

        :return: nodes
        :rtype: ``dict``
        """
        action = "ReadPublicIps"
        return self._call_api(action, data)

    def ex_list_public_ip_ranges(self, dry_run: bool = False):
        """
        Lists available regions details.

        :param      dry_run: If true, checks whether you have the
        required permissions to perform the action.
        :type       dry_run: ``bool``

        :return: regions details
        :rtype: ``dict``
        """
        action = "ReadPublicIpRanges"
        data = json.dumps({"DryRun": dry_run})
        return self._call_api(action, data)

    def ex_attach_public_ip(self,
                            allow_relink: bool = None,
                            dry_run: bool = False,
                            nic_id: str = None,
                            vm_id: str = None,
                            public_ip: str = None,
                            public_ip_id: str = None,
                            ):
        """
        Attach public ip to a node.

        :param      allow_relink: If true, allows the EIP to be associated
        with the VM or NIC that you specify even if
        it is already associated with another VM or NIC.
        :type       allow_relink: ``bool``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :param      nic_id:(Net only) The ID of the NIC. This parameter is
        required if the VM has more than one NIC attached. Otherwise,
        you need to specify the VmId parameter instead.
        You cannot specify both parameters
        at the same time.
        :type       nic_id: ``str``

        :param      vm_id: the ID of the VM
        :type       nic_id: ``str``

        :param      public_ip: The EIP. In the public Cloud, this parameter
        is required.
        :type       public_ip: ``str``

        :param      public_ip_id: The allocation ID of the EIP. In a Net,
        this parameter is required.
        :type       public_ip_id: ``str``

        :return: the attached volume
        :rtype: ``dict``
        """
        action = "LinkPublicIp"
        data = {"DryRun": dry_run}
        if public_ip is not None:
            data.update({"PublicIp": public_ip})
        if public_ip_id is not None:
            data.update({"PublicIpId": public_ip_id})
        if nic_id is not None:
            data.update({"NicId": nic_id})
        if vm_id is not None:
            data.update({"VmId": vm_id})
        if allow_relink is not None:
            data.update({"AllowRelink": allow_relink})
        data = json.dumps(data)
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def ex_detach_public_ip(self,
                            public_ip: str = None,
                            link_public_ip_id: str = None,
                            dry_run: bool = False):
        """
        Detach public ip from a node.

        :param      public_ip: (Required in a Net) The ID representing the
        association of the EIP with the VM or the NIC
        :type       public_ip: ``str``

        :param      link_public_ip_id: (Required in a Net) The ID
        representing the association of the EIP with the
        VM or the NIC.
        :type       link_public_ip_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: the attached volume
        :rtype: ``dict``
        """
        action = "UnlinkPublicIp"
        data = {"DryRun": dry_run}
        if public_ip is not None:
            data.update({"PublicIp": public_ip})
        if link_public_ip_id is not None:
            data.update({"LinkPublicIpId": link_public_ip_id})
        data = json.dumps(data)
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def create_node(self,
                    image: NodeImage,
                    name: str = None,
                    ex_dry_run: bool = False,
                    ex_block_device_mapping: dict = None,
                    ex_boot_on_creation: bool = True,
                    ex_bsu_optimized: bool = True,
                    ex_client_token: str = None,
                    ex_deletion_protection: bool = False,
                    ex_keypair_name: str = None,
                    ex_max_vms_count: int = None,
                    ex_min_vms_count: int = None,
                    ex_nics: dict = None,
                    ex_performance: str = None,
                    ex_placement: dict = None,
                    ex_private_ips: [str] = None,
                    ex_security_group_ids: [str] = None,
                    ex_security_groups: [str] = None,
                    ex_subnet_id: str = None,
                    ex_user_data: str = None,
                    ex_vm_initiated_shutdown_behavior: str = None,
                    ex_vm_type: str = None
                    ):
        """
        Create a new instance.

        :param      image: The image used to create the VM.
        :type       image: ``NodeImage``

        :param      name: The name of the Node.
        :type       name: ``str``

        :param      ex_dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       ex_dry_run: ``bool``

        :param      ex_block_device_mapping: One or more block device mappings.
        :type       ex_block_device_mapping: ``dict``

        :param      ex_boot_on_creation: By default or if true, the VM is
        started on creation. If false, the VM is
        stopped on creation.
        :type       ex_boot_on_creation: ``bool``

        :param      ex_bsu_optimized: If true, the VM is created with optimized
        BSU I/O.
        :type       ex_bsu_optimized: ``bool``

        :param      ex_client_token: A unique identifier which enables you to
        manage the idempotency.
        :type       ex_client_token: ``bool``

        :param      ex_deletion_protection: If true, you cannot terminate the
        VM using Cockpit, the CLI or the API.
        If false, you can.
        :type       ex_deletion_protection: ``bool``

        :param      ex_keypair_name: The name of the keypair.
        :type       ex_keypair_name: ``str``

        :param      ex_max_vms_count: The maximum number of VMs you want to
        create. If all the VMs cannot be created, the
        largest possible number of VMs above MinVmsCount is created.
        :type       ex_max_vms_count: ``integer``

        :param      ex_min_vms_count: The minimum number of VMs you want to
        create. If this number of VMs cannot be
        created, no VMs are created.
        :type       ex_min_vms_count: ``integer``

        :param      ex_nics: One or more NICs. If you specify this parameter,
        you must define one NIC as the primary
        network interface of the VM with 0 as its device number.
        :type       ex_nics: ``dict``

        :param      ex_performance: The performance of the VM (standard | high
        | highest).
        :type       ex_performance: ``str``

        :param      ex_placement: Information about the placement of the VM.
        :type       ex_placement: ``dict``

        :param      ex_private_ips: One or more private IP addresses of the VM.
        :type       ex_private_ips: ``list``

        :param      ex_security_group_ids: One or more IDs of security group
        for the VMs.
        :type       ex_security_group_ids: ``list``

        :param      ex_security_groups: One or more names of security groups
        for the VMs.
        :type       ex_security_groups: ``list``

        :param      ex_subnet_id: The ID of the Subnet in which you want to
        create the VM.
        :type       ex_subnet_id: ``str``

        :param      ex_user_data: Data or script used to add a specific
        configuration to the VM. It must be base64-encoded.
        :type       ex_user_data: ``str``

        :param      ex_vm_initiated_shutdown_behavior: The VM behavior when
        you stop it. By default or if set to stop, the
        VM stops. If set to restart, the VM stops then automatically restarts.
        If set to terminate, the VM stops and is terminated.
        create the VM.
        :type       ex_vm_initiated_shutdown_behavior: ``str``

        :param      ex_vm_type: The type of VM (t2.small by default).
        :type       ex_vm_type: ``str``

        :return: the created instance
        :rtype: ``dict``
        """
        data = {
            "DryRun": ex_dry_run,
            "BootOnCreation": ex_boot_on_creation,
            "BsuOptimized": ex_bsu_optimized,
            "ImageId": image.id
        }
        if ex_block_device_mapping is not None:
            data.update({"BlockDeviceMappings": ex_block_device_mapping})
        if ex_client_token is not None:
            data.update({"ClientToken": ex_client_token})
        if ex_deletion_protection is not None:
            data.update({"DeletionProtection": ex_deletion_protection})
        if ex_keypair_name is not None:
            data.update({"KeypairName": ex_keypair_name})
        if ex_max_vms_count is not None:
            data.update({"MaxVmsCount": ex_max_vms_count})
        if ex_min_vms_count is not None:
            data.update({"MinVmsCount": ex_min_vms_count})
        if ex_nics is not None:
            data.update({"Nics": ex_nics})
        if ex_performance is not None:
            data.update({"Performance": ex_performance})
        if ex_placement is not None:
            data.update({"Placement": ex_placement})
        if ex_private_ips is not None:
            data.update({"PrivateIps": ex_private_ips})
        if ex_security_group_ids is not None:
            data.update({"SecurityGroupIds": ex_security_group_ids})
        if ex_security_groups is not None:
            data.update({"SecurityGroups": ex_security_groups})
        if ex_user_data is not None:
            data.update({"UserData": ex_user_data})
        if ex_vm_initiated_shutdown_behavior is not None:
            data.update({
                "VmInstantiatedShutdownBehavior":
                    ex_vm_initiated_shutdown_behavior
            })
        if ex_vm_type is not None:
            data.update({"VmType": ex_vm_type})
        if ex_subnet_id is not None:
            data.update({"SubnetId": ex_subnet_id})
        action = "CreateVms"
        data = json.dumps(data)
        node = self._to_node(self._call_api(action, data).json()["Vms"][0])
        if name is not None:
            action = "CreateTags"
            data = {
                "DryRun": ex_dry_run,
                "ResourceIds": [node.id],
                "Tags": {
                    "Key": "Name",
                    "Value": name
                }
            }
            data = json.dumps(data)
            if self._call_api(action, data).status_code != 200:
                return False
            action = "ReadVms"
            data = {
                "DryRun": ex_dry_run,
                "Filters": {
                    "VmIds": [node.id]
                }
            }
            return self._to_node(
                self._call_api(action, json.dumps(data)).json()["Vms"][0]
            )
        return node

    def reboot_node(self, node: Node):
        """
        Reboot instance.

        :param      node: VM(s) you want to reboot (required)
        :type       node: ``list``

        :return: the rebooted instances
        :rtype: ``dict``
        """
        action = "RebootVms"
        data = json.dumps({"VmIds": [node.id]})
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def start_node(self, node: Node):
        """
                Start a Vm.

                :param      node: the  VM(s)
                            you want to start (required)
                :type       node: ``Node``

                :return: the rebooted instances
                :rtype: ``dict``
                """
        action = "StartVms"
        data = json.dumps({"VmIds": [node.id]})
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def stop_node(self, node: Node):
        """
                Stop a Vm.

                :param      node: the  VM(s)
                            you want to stop (required)
                :type       node: ``Node``

                :return: the rebooted instances
                :rtype: ``dict``
                """
        action = "StopVms"
        data = json.dumps({"VmIds": [node.id]})
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def list_nodes(self, ex_data: str = "{}"):
        """
        List all nodes.

        :return: nodes
        :rtype: ``dict``
        """
        action = "ReadVms"
        return self._to_nodes(self._call_api(action, ex_data).json()["Vms"])

    def destroy_node(self, node: Node):
        """
        Delete instance.

        :param      node: one or more IDs of VMs (required)
        :type       node: ``Node``

        :return: request
        :rtype: ``dict``
        """
        action = "DeleteVms"
        data = json.dumps({"VmIds": node.id})
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def create_image(
        self,
        ex_architecture: str = None,
        node: Node = None,
        name: str = None,
        description: str = None,
        ex_block_device_mapping: dict = None,
        ex_no_reboot: bool = False,
        ex_root_device_name: str = None,
        ex_dry_run: bool = False,
        ex_source_region_name: str = None,
        ex_file_location: str = None
    ):
        """
        Create a new image.

        :param      node: a valid Node object
        :type       node: ``str``

        :param      ex_architecture: The architecture of the OMI (by default,
        i386).
        :type       ex_architecture: ``str``

        :param      description: a description for the new OMI
        :type       description: ``str``

        :param      name: A unique name for the new OMI.
        :type       name: ``str``

        :param      ex_block_device_mapping: One or more block device mappings.
        :type       ex_block_device_mapping: ``dict``

        :param      ex_no_reboot: If false, the VM shuts down before creating
        the OMI and then reboots.
        If true, the VM does not.
        :type       ex_no_reboot: ``bool``

        :param      ex_root_device_name: The name of the root device.
        :type       ex_root_device_name: ``str``

        :param      ex_source_region_name: The name of the source Region,
        which must be the same
        as the Region of your account.
        :type       ex_source_region_name: ``str``

        :param      ex_file_location: The pre-signed URL of the OMI manifest
        file, or the full path to the OMI stored in
        an OSU bucket. If you specify this parameter, a copy of the OMI is
        created in your account.
        :type       ex_file_location: ``str``

        :param      ex_dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       ex_dry_run: ``bool``

        :return: the created image
        :rtype: ``dict``
        """
        data = {
            "DryRun": ex_dry_run,
            "NoReboot": ex_no_reboot,
        }
        if ex_block_device_mapping is not None:
            data.update({"BlockDeviceMappings": ex_block_device_mapping})
        if name is not None:
            data.update({"ImageName": name})
        if description is not None:
            data.update({"Description": description})
        if node.id is not None:
            data.update({"VmId": node.id})
        if ex_root_device_name is not None:
            data.update({"RootDeviceName": ex_root_device_name})
        if ex_source_region_name is not None:
            data.update({"SourceRegionName": ex_source_region_name})
        if ex_file_location is not None:
            data.update({"FileLocation": ex_file_location})
        data = json.dumps(data)
        action = "CreateImage"
        response = self._call_api(action, data)
        return self._to_node_image(response.json()["Image"])

    def list_images(self, ex_data: str = "{}"):
        """
        List all images.

        :return: images
        :rtype: ``dict``
        """
        action = "ReadImages"
        response = self._call_api(action, ex_data)
        return self._to_node_images(response.json()["Images"])

    def get_image(self, image_id: str):
        """
        Get a specific image.

        :param      image_id: the ID of the image you want to select (required)
        :type       image_id: ``str``

        :return: the selected image
        :rtype: ``dict``
        """
        action = "ReadImages"
        data = '{"Filters": {"ImageIds": ["' + image_id + '"]}}'
        response = self._call_api(action, data)
        return self._to_node_image(response.json()["Images"][0])

    def delete_image(self, node_image: NodeImage):
        """
        Delete an image.

        :param      node_image: the ID of the OMI you want to delete (required)
        :type       node_image: ``str``

        :return: request
        :rtype: ``dict``
        """
        action = "DeleteImage"
        data = '{"ImageId": "' + node_image.id + '"}'
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def create_key_pair(self,
                        name: str,
                        ex_dry_run: bool = False,
                        ex_public_key: str = None):
        """
        Create a new key pair.

        :param      name: A unique name for the keypair, with a maximum
        length of 255 ASCII printable characters.
        :type       name: ``str``

        :param      ex_dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       ex_dry_run: ``bool``

        :param      ex_public_key: The public key. It must be base64-encoded.
        :type       ex_public_key: ``str``

        :return: the created key pair
        :rtype: ``dict``
        """
        data = {
            "KeypairName": name,
            "DryRun": ex_dry_run,
        }
        if ex_public_key is not None:
            data.update({"PublicKey": ex_public_key})
        data = json.dumps(data)
        action = "CreateKeypair"
        response = self._call_api(action, data)
        return self._to_key_pair(response.json()["Keypair"])

    def list_key_pairs(self, ex_data: str = "{}"):
        """
        List all key pairs.

        :return: key pairs
        :rtype: ``dict``
        """
        action = "ReadKeypairs"
        response = self._call_api(action, ex_data)
        return self._to_key_pairs(response.json()["Keypairs"])

    def get_key_pair(self, name: str):
        """
        Get a specific key pair.

        :param      name: the name of the key pair
                    you want to select (required)
        :type       name: ``str``

        :return: the selected key pair
        :rtype: ``dict``
        """
        action = "ReadKeypairs"
        data = '{"Filters": {"KeypairNames" : ["' + name + '"]}}'
        response = self._call_api(action, data)
        return self._to_key_pair(response.json()["Keypairs"][0])

    def delete_key_pair(self, key_pair: KeyPair):
        """
        Delete a key pair.

        :param      key_pair: the name of the keypair
        you want to delete (required)
        :type       key_pair: ``KeyPair``

        :return: bool
        :rtype: ``bool``
        """
        action = "DeleteKeypair"
        data = '{"KeypairName": "' + key_pair.name + '"}'
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def create_volume_snapshot(
        self,
        ex_description: str = None,
        ex_dry_run: bool = False,
        ex_file_location: str = None,
        ex_snapshot_size: int = None,
        ex_source_region_name: str = None,
        ex_source_snapshot: VolumeSnapshot = None,
        volume: StorageVolume = None
    ):
        """
        Create a new volume snapshot.

        :param      ex_description: a description for the new OMI
        :type       ex_description: ``str``

        :param      ex_snapshot_size: The size of the snapshot created in your
        account, in bytes. This size must be
        exactly the same as the source snapshot one.
        :type       ex_snapshot_size: ``integer``

        :param      ex_source_snapshot: The ID of the snapshot you want to
        copy.
        :type       ex_source_snapshot: ``str``

        :param      volume: The ID of the volume you want to create a
        snapshot of.
        :type       volume: ``str``

        :param      ex_source_region_name: The name of the source Region,
        which must be the same as the Region of your account.
        :type       ex_source_region_name: ``str``

        :param      ex_file_location: The pre-signed URL of the OMI manifest
        file, or the full path to the OMI stored in
        an OSU bucket. If you specify this parameter, a copy of the OMI is
        created in your account.
        :type       ex_file_location: ``str``

        :param      ex_dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       ex_dry_run: ``bool``

        :return: the created snapshot
        :rtype: ``dict``
        """
        data = {
            "DryRun": ex_dry_run,
        }
        if ex_description is not None:
            data.update({"Description": ex_description})
        if ex_file_location is not None:
            data.update({"FileLocation": ex_file_location})
        if ex_snapshot_size is not None:
            data.update({"SnapshotSize": ex_snapshot_size})
        if ex_source_region_name is not None:
            data.update({"SourceRegionName": ex_source_region_name})
        if ex_source_snapshot is not None:
            data.update({"SourceSnapshotId": ex_source_snapshot.id})
        if volume is not None:
            data.update({"VolumeId": volume.id})
        data = json.dumps(data)
        action = "CreateSnapshot"
        response = self._call_api(action, data)
        return self._to_snapshot(response.json()["Volume"])

    def list_snapshots(self, ex_data: str = "{}"):
        """
        List all volume snapshots.

        :return: snapshots
        :rtype: ``dict``
        """
        action = "ReadSnapshots"
        response = self._call_api(action, ex_data)
        return self._to_snapshots(response.json()["Snapshots"])

    def list_volume_snapshots(self, volume):
        """
        List all snapshot for a given volume.

        :param     volume: the volume from which to look for snapshots
        :type      volume: StorageVolume

        :rtype: ``list`` of :class ``VolumeSnapshot``
        """
        action = "ReadSnapshots"
        data = {
            "Filters": {
                "VolumeIds": [volume.id]
            }
        }
        response = self._call_api(action, data).json()["Snapshots"]
        return self._to_snapshots(response)

    def destroy_volume_snapshot(self, snapshot: VolumeSnapshot):
        """
        Delete a volume snapshot.

        :param      snapshot: the ID of the snapshot
                    you want to delete (required)
        :type       snapshot: ``VolumeSnapshot``

        :return: request
        :rtype: ``bool``
        """
        action = "DeleteSnapshot"
        data = '{"SnapshotId": "' + snapshot.id + '"}'
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def create_volume(
        self,
        ex_subregion_name: str,
        ex_dry_run: bool = False,
        ex_iops: int = None,
        size: int = None,
        snapshot: VolumeSnapshot = None,
        ex_volume_type: str = None,
    ):
        """
        Create a new volume.

        :param      snapshot: the ID of the snapshot from which
                    you want to create the volume (required)
        :type       snapshot: ``str``

        :param      ex_dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       ex_dry_run: ``bool``

        :param      size: the size of the volume, in gibibytes (GiB),
                    the maximum allowed size for a volume is 14,901 GiB
        :type       size: ``int``

        :param      ex_subregion_name: The Subregion in which you want to
        create the volume.
        :type       ex_subregion_name: ``str``

        :param      ex_volume_type: the type of volume you want to create (io1
        | gp2 | standard)
        :type       ex_volume_type: ``str``

        :param      ex_iops: The number of I/O operations per second (IOPS).
        This parameter must be specified only if
        you create an io1 volume. The maximum number of IOPS allowed for io1
        volumes is 13000.
        :type       ex_iops: ``integer``

        :return: the created volume
        :rtype: ``dict``
        """
        data = {
            "DryRun": ex_dry_run,
            "SubregionName": ex_subregion_name
        }
        if ex_iops is not None:
            data.update({"Iops": ex_iops})
        if size is not None:
            data.update({"Size": size})
        if snapshot is not None:
            data.update({"SnapshotId": snapshot.id})
        if ex_volume_type is not None:
            data.update({"VolumeType": ex_volume_type})
        data = json.dumps(data)
        action = "CreateVolume"
        response = self._call_api(action, data)
        return self._to_volume(response.json()["Volume"])

    def list_volumes(self, ex_data: str = "{}"):
        """
        List all volumes.
        :rtype: ``list`` of :class:`.StorageVolume`
        """
        action = "ReadVolumes"
        response = self._call_api(action, ex_data)
        return self._to_volumes(response.json()["Volumes"])

    def destroy_volume(self, volume: StorageVolume):
        """
        Delete a volume.

        :param      volume: the ID of the volume
                    you want to delete (required)
        :type       volume: ``StorageVolume``

        :return: request
        :rtype: ``bool``
        """
        action = "DeleteVolume"
        data = '{"VolumeId": "' + volume.id + '"}'
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def attach_volume(
        self,
        node: Node,
        volume: StorageVolume,
        device: str = None
    ):
        """
        Attach a volume to a node.

        :param      node: the ID of the VM you want
                    to attach the volume to (required)
        :type       node: ``Node``

        :param      volume: the ID of the volume
                    you want to attach (required)
        :type       volume: ``StorageVolume``

        :param      device: the name of the device (required)
        :type       device: ``str``

        :return: the attached volume
        :rtype: ``dict``
        """
        action = "LinkVolume"
        data = json.dumps({
            "VmId": node.id,
            "VolumeId": volume.id,
            "DeviceName": device
        })
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def detach_volume(self,
                      volume: StorageVolume,
                      ex_dry_run: bool = False,
                      ex_force_unlink: bool = False):
        """
        Detach a volume from a node.

        :param      volume: the ID of the volume you want to detach
        (required)
        :type       volume: ``str``

        :param      ex_force_unlink: Forces the detachment of the volume in
        case of previous failure.
        Important: This action may damage your data or file systems.
        :type       ex_force_unlink: ``bool``

        :param      ex_dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       ex_dry_run: ``bool``

        :return: the attached volume
        :rtype: ``dict``
        """
        action = "UnlinkVolume"
        data = {"DryRun": ex_dry_run, "VolumeId": volume.id}
        if ex_force_unlink is not None:
            data.update({"ForceUnlink": ex_force_unlink})
        data = json.dumps(data)
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def ex_check_account(
        self,
        login: str,
        password: str,
        dry_run: bool = False,
    ):
        """
        Validates the authenticity of the account.

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :param      login: the login of the account
        :type       login: ``str``

        :param      password: the password of the account
        :type       password: ``str``

        :param      dry_run: the password of the account
        :type       dry_run: ``bool``

        :return: True if the action successful
        :rtype: ``bool``
        """
        action = "CheckAuthentication"
        data = {"DryRun": dry_run, "Login": login, "Password": password}
        if self._call_api(action, json.dumps(data)).status_code == 200:
            return True
        return False

    def ex_read_account(self, dry_run: bool = False):
        """
        Gets information about the account that sent the request.

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: the account information
        :rtype: ``dict``
        """
        action = "ReadAccounts"
        data = json.dumps({"DryRun": dry_run})
        return self._call_api(action, data).json()["Accounts"][0]

    def ex_create_account(
        self,
        city: str = None,
        company_name: str = None,
        country: str = None,
        customer_id: str = None,
        email: str = None,
        first_name: str = None,
        last_name: str = None,
        zip_code: str = None,
        job_title: str = None,
        mobile_number: str = None,
        phone_number: str = None,
        state_province: str = None,
        vat_number: str = None,
        dry_run: bool = False,
    ):
        """
        Creates a new 3DS OUTSCALE account.

        You need 3DS OUTSCALE credentials and the appropriate quotas to
        create a new account via API. To get quotas, you can send an email
        to sales@outscale.com.
        If you want to pass a numeral value as a string instead of an
        integer, you must wrap your string in additional quotes
        (for example, '"92000"').

        :param      city: The city of the account owner.
        :type       city: ``str``

        :param      company_name: The name of the company for the account.
        permissions to perform the action.
        :type       company_name: ``str``

        :param      country: The country of the account owner.
        :type       country: ``str``

        :param      customer_id: The ID of the customer. It must be 8 digits.
        :type       customer_id: ``str``

        :param      email: The email address for the account.
        :type       email: ``str``

        :param      first_name: The first name of the account owner.
        :type       first_name: ``str``

        :param      last_name: The last name of the account owner.
        :type       last_name: ``str``

        :param      zip_code: The ZIP code of the city.
        :type       zip_code: ``str``

        :param      job_title: The job title of the account owner.
        :type       job_title: ``str``

        :param      mobile_number: The mobile phone number of the account
        owner.
        :type       mobile_number: ``str``

        :param      phone_number: The landline phone number of the account
        owner.
        :type       phone_number: ``str``

        :param      state_province: The state/province of the account.
        :type       state_province: ``str``

        :param      vat_number: The value added tax (VAT) number for
        the account.
        :type       vat_number: ``str``

        :param      dry_run: the password of the account
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "CreateAccount"
        data = {"DryRun": dry_run}
        if city is not None:
            data.update({"City": city})
        if company_name is not None:
            data.update({"CompanyName": company_name})
        if country is not None:
            data.update({"Country": country})
        if customer_id is not None:
            data.update({"CustomerId": customer_id})
        if email is not None:
            data.update({"Email": email})
        if first_name is not None:
            data.update({"FirstName": first_name})
        if last_name is not None:
            data.update({"LastName": last_name})
        if zip_code is not None:
            data.update({"ZipCode": zip_code})
        if job_title is not None:
            data.update({"JobTitle": job_title})
        if mobile_number is not None:
            data.update({"MobileNumber": mobile_number})
        if phone_number is not None:
            data.update({"PhoneNumber": phone_number})
        if state_province is not None:
            data.update({"StateProvince": state_province})
        if vat_number is not None:
            data.update({"VatNumber": vat_number})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return response.json()

    def ex_update_account(
        self,
        city: str = None,
        company_name: str = None,
        country: str = None,
        email: str = None,
        first_name: str = None,
        last_name: str = None,
        zip_code: str = None,
        job_title: str = None,
        mobile_number: str = None,
        phone_number: str = None,
        state_province: str = None,
        vat_number: str = None,
        dry_run: bool = False,
    ):
        """
        Creates a new 3DS OUTSCALE account.

        You need 3DS OUTSCALE credentials and the appropriate quotas to
        create a new account via API. To get quotas, you can send an email
        to sales@outscale.com.
        If you want to pass a numeral value as a string instead of an
        integer, you must wrap your string in additional quotes
        (for example, '"92000"').

        :param      city: The city of the account owner.
        :type       city: ``str``

        :param      company_name: The name of the company for the account.
        permissions to perform the action.
        :type       company_name: ``str``

        :param      country: The country of the account owner.
        :type       country: ``str``

        :param      email: The email address for the account.
        :type       email: ``str``

        :param      first_name: The first name of the account owner.
        :type       first_name: ``str``

        :param      last_name: The last name of the account owner.
        :type       last_name: ``str``

        :param      zip_code: The ZIP code of the city.
        :type       zip_code: ``str``

        :param      job_title: The job title of the account owner.
        :type       job_title: ``str``

        :param      mobile_number: The mobile phone number of the account
        owner.
        :type       mobile_number: ``str``

        :param      phone_number: The landline phone number of the account
        owner.
        :type       phone_number: ``str``

        :param      state_province: The state/province of the account.
        :type       state_province: ``str``

        :param      vat_number: The value added tax (VAT) number for
        the account.
        :type       vat_number: ``str``

        :param      dry_run: the password of the account
        :type       dry_run: ``bool``

        :return: The new account information
        :rtype: ``dict``
        """
        action = "UpdateAccount"
        data = {"DryRun": dry_run}
        if city is not None:
            data.update({"City": city})
        if company_name is not None:
            data.update({"CompanyName": company_name})
        if country is not None:
            data.update({"Country": country})
        if email is not None:
            data.update({"Email": email})
        if first_name is not None:
            data.update({"FirstName": first_name})
        if last_name is not None:
            data.update({"LastName": last_name})
        if zip_code is not None:
            data.update({"ZipCode": zip_code})
        if job_title is not None:
            data.update({"JobTitle": job_title})
        if mobile_number is not None:
            data.update({"MobileNumber": mobile_number})
        if phone_number is not None:
            data.update({"PhoneNumber": phone_number})
        if state_province is not None:
            data.update({"StateProvince": state_province})
        if vat_number is not None:
            data.update({"VatNumber": vat_number})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["Account"]
        return response.json()

    def ex_reset_account_password(
        self,
        password: str = "",
        token: str = "",
        dry_run: bool = False,
    ):
        """
        Sends an email to the email address provided for the account with a
        token to reset your password.

        :param      password: The new password for the account.
        :type       password: ``str``

        :param      token: The token you received at the email address
        provided for the account.
        :type       token: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "ResetAccountPassword"
        data = json.dumps({
            "DryRun": dry_run, "Password": password, "Token": token
        })
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def ex_send_reset_password_email(
        self,
        email: str,
        dry_run: bool = False,
    ):
        """
        Replaces the account password with the new one you provide.
        You must also provide the token you received by email when asking for
        a password reset using the SendResetPasswordEmail method.

        :param      email: The email address provided for the account.
        :type       email: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "SendResetPasswordEmail"
        data = json.dumps({
            "DryRun": dry_run, "Email": email
        })
        if self._call_api(action, data).status_code == 200:
            return True
        return False

    def ex_create_tag(
        self,
        resource_ids: list,
        tag_key: str = None,
        tag_value: str = None,
        dry_run: bool = False,
    ):
        """
        Adds one tag to the specified resources.
        If a tag with the same key already exists for the resource,
        the tag value is replaced.
        You can tag the following resources using their IDs:

        :param      resource_ids: One or more resource IDs. (required)
        :type       resource_ids: ``list``

        :param      tag_key: The key of the tag, with a minimum of 1 character.
        (required)
        :type       tag_key: ``str``

        :param      tag_value: The value of the tag, between
        0 and 255 characters. (required)
        :type       tag_value: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action. (required)
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "CreateTags"
        data = {"DryRun": dry_run, "ResourceIds": resource_ids, "Tags": []}
        if tag_key is not None and tag_value is not None:
            data["Tags"].append({"Key": tag_key, "Value": tag_value})
        if self._call_api(action, json.dumps(data)).status_code == 200:
            return True
        return False

    def ex_create_tags(
        self,
        resource_ids: list,
        tags: list = [],
        dry_run: bool = False,
    ):
        """
        Adds one or more tags to the specified resources.
        If a tag with the same key already exists for the resource,
        the tag value is replaced.
        You can tag the following resources using their IDs:

        :param      resource_ids: One or more resource IDs. (required)
        :type       resource_ids: ``list``

        :param      tags: The key of the tag, with a minimum of 1 character.
        (required)
        :type       tags: ``list`` of ``dict``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "CreateTags"
        data = {"DryRun": dry_run, "ResourceIds": resource_ids, "Tags": tags}
        if self._call_api(action, json.dumps(data)).status_code == 200:
            return True
        return False

    def ex_delete_tags(
        self,
        resource_ids: list,
        tags: list = [],
        dry_run: bool = False,
    ):
        """
        Deletes one or more tags from the specified resources.

        :param      resource_ids: One or more resource IDs. (required)
        :type       resource_ids: ``list``

        :param      tags: The key of the tag, with a minimum of 1 character.
        (required)
        :type       tags: ``list`` of ``dict``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteTags"
        data = {"DryRun": dry_run, "ResourceIds": resource_ids, "Tags": tags}
        if self._call_api(action, json.dumps(data)).status_code == 200:
            return True
        return False

    def ex_list_tags(
        self,
        resource_ids: list = None,
        resource_types: list = None,
        keys: list = None,
        values: list = None,
        dry_run: bool = False
    ):
        """
        Lists one or more tags for your resources.

        :param      resource_ids: One or more resource IDs.
        :type       resource_ids: ``list``

        :param      resource_types: One or more resource IDs.
        :type       resource_types: ``list``

        :param      keys: One or more resource IDs.
        :type       keys: ``list``

        :param      values: One or more resource IDs.
        :type       values: ``list``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: list of tags
        :rtype: ``list`` of ``dict``
        """
        action = "ReadTags"
        data = {"Filters": {}, "DryRun": dry_run}
        if resource_ids is not None:
            data["Filters"].update({"ResourceIds": resource_ids})
        if resource_types is not None:
            data["Filters"].update({"ResourceTypes": resource_types})
        if keys is not None:
            data["Filters"].update({"Keys": keys})
        if values is not None:
            data["Filters"].update({"Values": values})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["Tags"]
        return response.json()

    def ex_create_access_key(
        self,
        expiration_date: datetime = None,
        dry_run: bool = False,
    ):
        """
        Creates a new secret access key and the corresponding access key ID
        for a specified user. The created key is automatically set to ACTIVE.

        :param      expiration_date: The date and time at which you want the
        access key to expire, in ISO 8601 format (for example,
        2017-06-14 or 2017-06-14T00:00:00Z). If not specified, the access key
        has no expiration date.
        :type       expiration_date: ``datetime``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: access key if action is successful
        :rtype: ``dict``
        """
        action = "CreateAccessKey"
        data = {"DryRun": dry_run}
        if expiration_date is not None:
            data.update({"ExpirationDate": expiration_date})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["AccessKey"]
        return response.json()

    def ex_delete_access_key(
        self,
        access_key_id: str,
        dry_run: bool = False,
    ):
        """
        Deletes the specified access key associated with the account
        that sends the request.

        :param      access_key_id: The ID of the access key you want to
        delete. (required)
        :type       access_key_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteAccessKey"
        data = {"DryRun": dry_run}
        if access_key_id is not None:
            data.update({"AccessKeyId": access_key_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_list_access_keys(
        self,
        access_key_ids: list = None,
        states: list = None,
        dry_run: bool = False,
    ):
        """
        Returns information about the access key IDs of a specified user.
        If the user does not have any access key ID, this action returns
        an empty list.

        :param      access_key_ids: The IDs of the access keys.
        :type       access_key_ids: ``list`` of ``str``

        :param      states: The states of the access keys (ACTIVE | INACTIVE).
        :type       states: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: ``list`` of Access Keys
        :rtype: ``list`` of ``dict``
        """
        action = "ReadAccessKeys"
        data = {"DryRun": dry_run, "Filters": {}}
        if access_key_ids is not None:
            data["Filters"].update({"AccessKeyIds": access_key_ids})
        if states is not None:
            data["Filters"].update({"States": states})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["AccessKeys"]
        return response.json()

    def ex_list_secret_access_key(
        self,
        access_key_id: str = None,
        dry_run: bool = False,
    ):
        """
        Gets information about the secret access key associated with
        the account that sends the request.

        :param      access_key_id: The ID of the access key. (required)
        :type       access_key_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: Access Key
        :rtype: ``dict``
        """
        action = "ReadSecretAccessKey"
        data = {"DryRun": dry_run}
        if access_key_id is not None:
            data.update({"AccessKeyId": access_key_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["AccessKey"]
        return response.json()

    def ex_update_access_key(
        self,
        access_key_id: str = None,
        state: str = None,
        dry_run: bool = False,
    ):
        """
        Modifies the status of the specified access key associated with
        the account that sends the request.
        When set to ACTIVE, the access key is enabled and can be used to
        send requests. When set to INACTIVE, the access key is disabled.

        :param      access_key_id: The ID of the access key. (required)
        :type       access_key_id: ``str``

        :param      state: The new state of the access key
        (ACTIVE | INACTIVE). (required)
        :type       state: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: Access Key
        :rtype: ``dict``
        """
        action = "UpdateAccessKey"
        data = {"DryRun": dry_run}
        if access_key_id is not None:
            data.update({"AccessKeyId": access_key_id})
        if state is not None:
            data.update({"State": state})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["AccessKey"]
        return response.json()

    def ex_create_client_gateway(
        self,
        bgp_asn: int = None,
        connection_type: str = None,
        public_ip: str = None,
        dry_run: bool = False,
    ):
        """
        Provides information about your client gateway.
        This action registers information to identify the client gateway that
        you deployed in your network.
        To open a tunnel to the client gateway, you must provide
        the communication protocol type, the valid fixed public IP address
        of the gateway, and an Autonomous System Number (ASN).

        :param      bgp_asn: An Autonomous System Number (ASN) used by
        the Border Gateway Protocol (BGP) to find the path to your
        client gateway through the Internet. (required)
        :type       bgp_asn: ``int`` (required)

        :param      connection_type: The communication protocol used to
        establish tunnel with your client gateway (only ipsec.1 is supported).
        (required)
        :type       connection_type: ``str``

        :param      public_ip: The public fixed IPv4 address of your
        client gateway. (required)
        :type       public_ip: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: Client Gateway as ``dict``
        :rtype: ``dict``
        """
        action = "CreateClientGateway"
        data = {"DryRun": dry_run}
        if bgp_asn is not None:
            data.update({"BgpAsn": bgp_asn})
        if connection_type is not None:
            data.update({"ConnectionType": connection_type})
        if public_ip is not None:
            data.update({"PublicIp": public_ip})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["ClientGateway"]
        return response.json()

    def ex_list_client_gateways(
        self,
        client_gateway_ids: list = None,
        bgp_asns: list = None,
        connection_types: list = None,
        public_ips: list = None,
        states: list = None,
        tag_keys: list = None,
        tag_values: list = None,
        tags: list = None,
        dry_run: bool = False,
    ):
        """
        Deletes a client gateway.
        You must delete the VPN connection before deleting the client gateway.

        :param      client_gateway_ids: The IDs of the client gateways.
        you want to delete. (required)
        :type       client_gateway_ids: ``list`` of ``str`

        :param      bgp_asns: The Border Gateway Protocol (BGP) Autonomous
        System Numbers (ASNs) of the connections.
        :type       bgp_asns: ``list`` of ``int``

        :param      connection_types: The types of communication tunnels
        used by the client gateways (only ipsec.1 is supported).
        (required)
        :type       connection_types: ``list```of ``str``

        :param      public_ips: The public IPv4 addresses of the
        client gateways.
        :type       public_ips: ``list`` of ``str``

        :param      states: The states of the client gateways
        (pending | available | deleting | deleted).
        :type       states: ``list`` of ``str``

        :param      tag_keys: The keys of the tags associated with
        the client gateways.
        :type       tag_keys: ``list`` of ``str``

        :param      tag_values: The values of the tags associated with the
        client gateways.
        :type       tag_values: ``list`` of ``str``

        :param      tags: TThe key/value combination of the tags
        associated with the client gateways, in the following
        format: "Filters":{"Tags":["TAGKEY=TAGVALUE"]}.
        :type       tags: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: Returns ``list`` of Client Gateway
        :rtype: ``list`` of ``dict``
        """
        action = "ReadClientGateways"
        data = {"DryRun": dry_run, "Filters": {}}
        if client_gateway_ids is not None:
            data["Filters"].update({"ClientGatewayIds": client_gateway_ids})
        if bgp_asns is not None:
            data["Filters"].update({"BgpAsns": bgp_asns})
        if connection_types is not None:
            data["Filters"].update({"ConnectionTypes": connection_types})
        if public_ips is not None:
            data["Filters"].update({"PublicIps": public_ips})
        if client_gateway_ids is not None:
            data["Filters"].update({"ClientGatewayIds": client_gateway_ids})
        if states is not None:
            data["Filters"].update({"States": states})
        if tag_keys is not None:
            data["Filters"].update({"TagKeys": tag_keys})
        if tag_values is not None:
            data["Filters"].update({"TagValues": tag_values})
        if tags is not None:
            data["Filters"].update({"Tags": tags})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["ClientGateways"]
        return response.json()

    def ex_delete_client_gateway(
        self,
        client_gateway_id: str = None,
        dry_run: bool = False,
    ):
        """
        Deletes a client gateway.
        You must delete the VPN connection before deleting the client gateway.

        :param      client_gateway_id: The ID of the client gateway
        you want to delete. (required)
        :type       client_gateway_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: Returns True if action is successful
        :rtype: ``bool``
        """
        action = "DeleteClientGateway"
        data = {"DryRun": dry_run}
        if client_gateway_id is not None:
            data.update({"ClientGatewayId": client_gateway_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_create_dhcp_options(
        self,
        domaine_name: str = None,
        domaine_name_servers: list = None,
        ntp_servers: list = None,
        dry_run: bool = False,
    ):
        """
        Creates a new set of DHCP options, that you can then associate
        with a Net using the UpdateNet method.

        :param      domaine_name: Specify a domain name
        (for example, MyCompany.com). You can specify only one domain name.
        :type       domaine_name: ``str``

        :param      domaine_name_servers: The IP addresses of domain name
        servers. If no IP addresses are specified, the OutscaleProvidedDNS
        value is set by default.
        :type       domaine_name_servers: ``list`` of ``str``

        :param      ntp_servers: The IP addresses of the Network Time
        Protocol (NTP) servers.
        :type       ntp_servers: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The created Dhcp Options
        :rtype: ``dict``
        """
        action = "CreateDhcpOptions"
        data = {"DryRun": dry_run}
        if domaine_name is not None:
            data.update({"DomaineName": domaine_name})
        if domaine_name_servers is not None:
            data.update({"DomaineNameServers": domaine_name_servers})
        if ntp_servers is not None:
            data.update({"NtpServers": ntp_servers})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["DhcpOptionsSet"]
        return response.json()

    def ex_delete_dhcp_options(
        self,
        dhcp_options_set_id: str = None,
        dry_run: bool = False,
    ):
        """
        Deletes a specified DHCP options set.
        Before deleting a DHCP options set, you must disassociate it from the
        Nets you associated it with. To do so, you need to associate with each
        Net a new set of DHCP options, or the default one if you do not want
        to associate any DHCP options with the Net.

        :param      dhcp_options_set_id: The ID of the DHCP options set
        you want to delete. (required)
        :type       dhcp_options_set_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteDhcpOptions"
        data = {"DryRun": dry_run}
        if dhcp_options_set_id is not None:
            data.update({"DhcpOptionsSetId": dhcp_options_set_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_list_dhcp_options(
        self,
        default: bool = None,
        dhcp_options_set_id: list = None,
        domaine_names: list = None,
        domaine_name_servers: list = None,
        ntp_servers: list = None,
        tag_keys: list = None,
        tag_values: list = None,
        tags: list = None,
        dry_run: bool = False,
    ):
        """
        Retrieves information about the content of one or more
        DHCP options sets.

        :param      default: SIf true, lists all default DHCP options set.
        If false, lists all non-default DHCP options set.
        :type       default: ``list`` of ``bool``

        :param      dhcp_options_set_id: The IDs of the DHCP options sets.
        :type       dhcp_options_set_id: ``list`` of ``str``

        :param      domaine_names: The domain names used for the DHCP
        options sets.
        :type       domaine_names: ``list`` of ``str``

        :param      domaine_name_servers: The domain name servers used for
        the DHCP options sets.
        :type       domaine_name_servers: ``list`` of ``str``

        :param      ntp_servers: The Network Time Protocol (NTP) servers used
        for the DHCP options sets.
        :type       ntp_servers: ``list`` of ``str``

        :param      tag_keys: The keys of the tags associated with the DHCP
        options sets.
        :type       ntp_servers: ``list`` of ``str``

        :param      tag_values: The values of the tags associated with the
        DHCP options sets.
        :type       tag_values: ``list`` of ``str``

        :param      tags: The key/value combination of the tags associated
        with the DHCP options sets, in the following format:
        "Filters":{"Tags":["TAGKEY=TAGVALUE"]}.
        :type       tags: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: a ``list`` of Dhcp Options
        :rtype: ``list`` of ``dict``
        """
        action = "ReadDhcpOptions"
        data = {"DryRun": dry_run, "Filters": {}}
        if default is not None:
            data["Filters"].update({"Default": default})
        if dhcp_options_set_id is not None:
            data["Filters"].update({"DhcpOptionsSetIds": dhcp_options_set_id})
        if domaine_names is not None:
            data["Filters"].update({"DomaineNames": domaine_names})
        if domaine_name_servers is not None:
            data["Filters"].update({
                "DomaineNameServers": domaine_name_servers
            })
        if ntp_servers is not None:
            data["Filters"].update({"NtpServers": ntp_servers})
        if tag_keys is not None:
            data["Filters"].update({"TagKeys": tag_keys})
        if tag_values is not None:
            data["Filters"].update({"TagValues": tag_values})
        if tags is not None:
            data["Filters"].update({"Tags": tags})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["DhcpOptionsSets"]
        return response.json()

    def ex_create_direct_link(
        self,
        bandwidth: str = None,
        direct_link_name: str = None,
        location: str = None,
        dry_run: bool = False,
    ):
        """
        Creates a new DirectLink between a customer network and a
        specified DirectLink location.

        :param      bandwidth: The bandwidth of the DirectLink
        (1Gbps | 10Gbps). (required)
        :type       bandwidth: ``str``

        :param      direct_link_name: The name of the DirectLink. (required)
        :type       direct_link_name: ``str``

        :param      location: The code of the requested location for
        the DirectLink, returned by the list_locations method.
        Protocol (NTP) servers.
        :type       location: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Direct Link
        :rtype: ``dict``
        """
        action = "CreateDirectLink"
        data = {"DryRun": dry_run}
        if bandwidth is not None:
            data.update({"Bandwidth": bandwidth})
        if direct_link_name is not None:
            data.update({"DirectLinkName": direct_link_name})
        if location is not None:
            data.update({"Location": location})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["DirectLink"]
        return response.json()

    def ex_delete_direct_link(
        self,
        direct_link_id: str = None,
        dry_run: bool = False,
    ):
        """
        Deletes a specified DirectLink.
        Before deleting a DirectLink, ensure that all your DirectLink
        interfaces related to this DirectLink are deleted.

        :param      direct_link_id: The ID of the DirectLink you want to
        delete. (required)
        :type       direct_link_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteDirectLink"
        data = {"DryRun": dry_run}
        if direct_link_id is not None:
            data.update({"DirectLinkId": direct_link_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_list_direct_link(
        self,
        direct_link_ids: list = None,
        dry_run: bool = False,
    ):
        """
        Lists all DirectLinks in the Region.

        :param      direct_link_ids: The IDs of the DirectLinks. (required)
        :type       direct_link_ids: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: ``list`` of  Direct Links
        :rtype: ``list`` of ``dict``
        """
        action = "DeleteDirectLink"
        data = {"DryRun": dry_run, "Filters": {}}
        if direct_link_ids is not None:
            data["Filters"].update({"DirectLinkIds": direct_link_ids})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["DirectLinks"]
        return response.json()

    def ex_create_direct_link_interface(
        self,
        direct_link_id: str = None,
        bgp_asn: int = None,
        bgp_key: str = None,
        client_private_ip: str = None,
        direct_link_interface_name: str = None,
        outscale_private_ip: str = None,
        virtual_gateway_id: str = None,
        vlan: int = None,
        dry_run: bool = False,
    ):
        """
        Creates a DirectLink interface.
        DirectLink interfaces enable you to reach one of your Nets through a
        virtual gateway.

        :param      direct_link_id: The ID of the existing DirectLink for which
        you want to create the DirectLink interface. (required)
        :type       direct_link_id: ``str``

        :param      bgp_asn: The BGP (Border Gateway Protocol) ASN (Autonomous
        System Number) on the customer's side of the DirectLink interface.
        (required)
        :type       bgp_asn: ``int``

        :param      bgp_key: The BGP authentication key.
        :type       bgp_key: ``str``

        :param      client_private_ip: The IP address on the customer's side
        of the DirectLink interface. (required)
        :type       client_private_ip: ``str``

        :param      direct_link_interface_name: The name of the DirectLink
        interface. (required)
        :type       direct_link_interface_name: ``str``

        :param      outscale_private_ip: The IP address on 3DS OUTSCALE's side
        of the DirectLink interface.
        :type       outscale_private_ip: ``str``

        :param      virtual_gateway_id:The ID of the target virtual gateway.
        (required)
        :type       virtual_gateway_id: ``str``

        :param      vlan: The VLAN number associated with the DirectLink
        interface. (required)
        :type       vlan: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Direct Link Interface
        :rtype: ``dict``
        """
        action = "CreateDirectLinkInterface"
        data = {"DryRun": dry_run, "DirectLinkInterface": {}}
        if direct_link_id is not None:
            data.update({"DirectLinkId": direct_link_id})
        if bgp_asn is not None:
            data["DirectLinkInterface"].update({"BgpAsn": bgp_asn})
        if bgp_key is not None:
            data["DirectLinkInterface"].update({"BgpKey": bgp_key})
        if client_private_ip is not None:
            data["DirectLinkInterface"].update({
                "ClientPrivateIp": client_private_ip
            })
        if direct_link_interface_name is not None:
            data["DirectLinkInterface"].update({
                "DirectLinkInterfaceName": direct_link_interface_name
            })
        if outscale_private_ip is not None:
            data["DirectLinkInterface"].update({
                "OutscalePrivateIp": outscale_private_ip
            })
        if virtual_gateway_id is not None:
            data["DirectLinkInterface"].update({
                "VirtualGatewayId": virtual_gateway_id
            })
        if vlan is not None:
            data["DirectLinkInterface"].update({
                "Vlan": vlan
            })
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["DirectLinkInterface"]
        return response.json()

    def ex_delete_direct_link_interface(
        self,
        direct_link_interface_id: str = None,
        dry_run: bool = False,
    ):
        """
        Deletes a specified DirectLink interface.

        :param      direct_link_interface_id: TThe ID of the DirectLink
        interface you want to delete. (required)
        :type       direct_link_interface_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteDirectLinkInterface"
        data = {"DryRun": dry_run}
        if direct_link_interface_id is not None:
            data.update({"DirectLinkInterfaceId": direct_link_interface_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_list_direct_link_interfaces(
        self,
        direct_link_ids: list = None,
        direct_link_interface_ids: list = None,
        dry_run: bool = False,
    ):
        """
        Lists all DirectLinks in the Region.

        :param      direct_link_interface_ids: The IDs of the DirectLink
        interfaces.
        :type       direct_link_interface_ids: ``list`` of ``str``

        :param      direct_link_ids: The IDs of the DirectLinks.
        :type       direct_link_ids: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: ``list`` of  Direct Link interfaces
        :rtype: ``list`` of ``dict``
        """
        action = "DeleteDirectLink"
        data = {"DryRun": dry_run, "Filters": {}}
        if direct_link_ids is not None:
            data["Filters"].update({
                "DirectLinkIds": direct_link_ids
            })
        if direct_link_interface_ids is not None:
            data["Filters"].update({
                "DirectLinkInterfaceIds": direct_link_interface_ids
            })
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["DirectLinkInterfaces"]
        return response.json()

    def ex_create_flexible_gpu(
        self,
        delete_on_vm_deletion: bool = None,
        generation: str = None,
        model_name: str = None,
        subregion_name: str = None,
        dry_run: bool = False,
    ):
        """
        Allocates a flexible GPU (fGPU) to your account.
        You can then attach this fGPU to a virtual machine (VM).

        :param      delete_on_vm_deletion: If true, the fGPU is deleted when
        the VM is terminated.
        :type       delete_on_vm_deletion: ``bool``

        :param      generation: The processor generation that the fGPU must be
        compatible with. If not specified, the oldest possible processor
        generation is selected (as provided by ReadFlexibleGpuCatalog for
        the specified model of fGPU).
        :type       generation: ``str``

        :param      model_name: The model of fGPU you want to allocate. For
        more information, see About Flexible GPUs:
        https://wiki.outscale.net/display/EN/About+Flexible+GPUs (required)
        :type       model_name: ``str``

        :param      subregion_name: The Subregion in which you want to create
        the fGPU. (required)
        :type       subregion_name: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Flexible GPU
        :rtype: ``dict``
        """
        action = "CreateFlexibleGpu"
        data = {"DryRun": dry_run, "DirectLinkInterface": {}}
        if delete_on_vm_deletion is not None:
            data.update({"DeleteOnVmDeletion": delete_on_vm_deletion})
        if generation is not None:
            data.update({"Generation": generation})
        if model_name is not None:
            data.update({"ModelName": model_name})
        if subregion_name is not None:
            data.update({
                "SubregionName": subregion_name
            })
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["FlexibleGpu"]
        return response.json()

    def ex_delete_flexible_gpu(
        self,
        flexible_gpu_id: str = None,
        dry_run: bool = False,
    ):
        """
        Releases a flexible GPU (fGPU) from your account.
        The fGPU becomes free to be used by someone else.

        :param      flexible_gpu_id: The ID of the fGPU you want
        to delete. (required)
        :type       flexible_gpu_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteFlexibleGpu"
        data = {"DryRun": dry_run}
        if flexible_gpu_id is not None:
            data.update({"FlexibleGpuId": flexible_gpu_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_unlink_flexible_gpu(
        self,
        flexible_gpu_id: str = None,
        dry_run: bool = False,
    ):
        """
        Detaches a flexible GPU (fGPU) from a virtual machine (VM).
        The fGPU is in the detaching state until the VM is stopped, after
        which it becomes available for allocation again.

        :param      flexible_gpu_id: The ID of the fGPU you want to attach.
        (required)
        :type       flexible_gpu_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "UnlinkFlexibleGpu"
        data = {"DryRun": dry_run}
        if flexible_gpu_id is not None:
            data.update({"FlexibleGpuId": flexible_gpu_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_link_flexible_gpu(
        self,
        flexible_gpu_id: str = None,
        vm_id: str = None,
        dry_run: bool = False,
    ):
        """
        Attaches one of your allocated flexible GPUs (fGPUs) to one of your
        virtual machines (VMs).
        The fGPU is in the attaching state until the VM is stopped, after
        which it becomes attached.

        :param      flexible_gpu_id: The ID of the fGPU you want to attach.
        (required)
        :type       flexible_gpu_id: ``str``

        :param      vm_id: The ID of the VM you want to attach the fGPU to.
        (required)
        :type       vm_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "LinkFlexibleGpu"
        data = {"DryRun": dry_run}
        if flexible_gpu_id is not None:
            data.update({"FlexibleGpuId": flexible_gpu_id})
        if vm_id is not None:
            data.update({"VmId": vm_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_list_flexible_gpu_catalog(
        self,
        dry_run: bool = False,
    ):
        """
        Lists all flexible GPUs available in the public catalog.

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: Returns the Flexible Gpu Catalog
        :rtype: ``list`` of ``dict``
        """
        action = "ReadFlexibleGpuCatalog"
        data = {"DryRun": dry_run}
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["FlexibleGpuCatalog"]
        return response.json()

    def ex_list_flexible_gpus(
        self,
        delete_on_vm_deletion: bool = None,
        flexible_gpu_ids: list = None,
        generations: list = None,
        model_names: list = None,
        states: list = None,
        subregion_names: list = None,
        vm_ids: list = None,
        dry_run: bool = False,
    ):
        """
        Lists one or more flexible GPUs (fGPUs) allocated to your account.

        :param      delete_on_vm_deletion: Indicates whether the fGPU is
        deleted when terminating the VM.
        :type       delete_on_vm_deletion: ``bool``

        :param      flexible_gpu_ids: One or more IDs of fGPUs.
        :type       flexible_gpu_ids: ``list`` of ``str``

        :param      generations: The processor generations that the fGPUs are
        compatible with.
        (required)
        :type       generations: ``list`` of ``str``

        :param      model_names: One or more models of fGPUs. For more
        information, see About Flexible GPUs:
        https://wiki.outscale.net/display/EN/About+Flexible+GPUs
        :type       model_names: ``list`` of ``str``

        :param      states: The states of the fGPUs
        (allocated | attaching | attached | detaching).
        :type       states: ``list`` of ``str``

        :param      subregion_names: The Subregions where the fGPUs are
        located.
        :type       subregion_names: ``list`` of ``str``

        :param      vm_ids: One or more IDs of VMs.
        :type       vm_ids: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: Returns the Flexible Gpu Catalog
        :rtype: ``list`` of ``dict``
        """
        action = "ReadFlexibleGpus"
        data = {"DryRun": dry_run, "Filters": {}}
        if delete_on_vm_deletion is not None:
            data["Filters"].update({
                "DeleteOnVmDeletion": delete_on_vm_deletion
            })
        if flexible_gpu_ids is not None:
            data["Filters"].update({"FlexibleGpuIds": flexible_gpu_ids})
        if generations is not None:
            data["Filters"].update({"Generations": generations})
        if model_names is not None:
            data["Filters"].update({"ModelNames": model_names})
        if states is not None:
            data["Filters"].update({"States": states})
        if subregion_names is not None:
            data["Filters"].update({"SubregionNames": subregion_names})
        if vm_ids is not None:
            data["Filters"].update({"VmIds": vm_ids})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["FlexibleGpus"]
        return response.json()

    def ex_update_flexible_gpu(
        self,
        delete_on_vm_deletion: bool = None,
        flexible_gpu_id: str = None,
        dry_run: bool = False,
    ):
        """
        Modifies a flexible GPU (fGPU) behavior.

        :param      delete_on_vm_deletion: If true, the fGPU is deleted when
        the VM is terminated.
        :type       delete_on_vm_deletion: ``bool``

        :param      flexible_gpu_id: The ID of the fGPU you want to modify.
        :type       flexible_gpu_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: the updated Flexible GPU
        :rtype: ``dict``
        """
        action = "UpdateFlexibleGpu"
        data = {"DryRun": dry_run, "DirectLinkInterface": {}}
        if delete_on_vm_deletion is not None:
            data.update({"DeleteOnVmDeletion": delete_on_vm_deletion})
        if flexible_gpu_id is not None:
            data.update({"FlexibleGpuId": flexible_gpu_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["FlexibleGpu"]
        return response.json()

    def ex_create_internet_service(
        self,
        dry_run: bool = False,
    ):
        """
        Creates an Internet service you can use with a Net.
        An Internet service enables your virtual machines (VMs) launched
        in a Net to connect to the Internet. By default, a Net includes
        an Internet service, and each Subnet is public. Every VM
        launched within a default Subnet has a private and a public IP
        addresses.

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Internet Service
        :rtype: ``dict``
        """
        action = "CreateInternetService"
        data = {"DryRun": dry_run, "DirectLinkInterface": {}}
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["InternetService"]
        return response.json()

    def ex_delete_internet_service(
        self,
        internet_service_id: str = None,
        dry_run: bool = False,
    ):
        """
        Deletes an Internet service.
        Before deleting an Internet service, you must detach it from any Net
        it is attached to.

        :param      internet_service_id: The ID of the Internet service you
        want to delete.(required)
        :type       internet_service_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteInternetService"
        data = {"DryRun": dry_run}
        if internet_service_id is not None:
            data.update({"InternetServiceId": internet_service_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_link_internet_service(
        self,
        internet_service_id: str = None,
        net_id: str = None,
        dry_run: bool = False,
    ):
        """
        Attaches an Internet service to a Net.
        To enable the connection between the Internet and a Net, you must
        attach an Internet service to this Net.

        :param      internet_service_id: The ID of the Internet service you
        want to attach. (required)
        :type       internet_service_id: ``str``

        :param      net_id: The ID of the Net to which you want to attach the
        Internet service. (required)
        :type       net_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "LinkInternetService"
        data = {"DryRun": dry_run}
        if internet_service_id is not None:
            data.update({"InternetServiceId": internet_service_id})
        if net_id is not None:
            data.update({"NetId": net_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_unlink_internet_service(
        self,
        internet_service_id: str = None,
        net_id: str = None,
        dry_run: bool = False,
    ):
        """
        Detaches an Internet service from a Net.
        This action disables and detaches an Internet service from a Net.
        The Net must not contain any running virtual machine (VM) using an
        External IP address (EIP).

        :param      internet_service_id: The ID of the Internet service you
        want to detach. (required)
        :type       internet_service_id: ``str``

        :param      net_id: The ID of the Net from which you want to detach
        the Internet service. (required)
        :type       net_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "UnlinkInternetService"
        data = {"DryRun": dry_run}
        if internet_service_id is not None:
            data.update({"InternetServiceId": internet_service_id})
        if net_id is not None:
            data.update({"NetId": net_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_list_internet_services(
        self,
        internet_service_ids: [str] = None,
        link_net_ids: [str] = None,
        link_states: [str] = None,
        tag_keys: [str] = None,
        tag_values: [str] = None,
        tags: [str] = None,
        dry_run: bool = False
    ):
        """
        Lists one or more of your Internet services.
        An Internet service enables your virtual machines (VMs) launched in a
        Net to connect to the Internet. By default, a Net includes an
        Internet service, and each Subnet is public. Every VM launched within
        a default Subnet has a private and a public IP addresses.

        :param      internet_service_ids: One or more filters.
        :type       internet_service_ids: ``list`` of ``str``

        :param      link_net_ids: The IDs of the Nets the Internet services
        are attached to.
        :type       link_net_ids: ``list`` of ``str``

        :param      link_states: The current states of the attachments
        between the Internet services and the Nets (only available,
        if the Internet gateway is attached to a VPC). (required)
        :type       link_states: ``list`` of ``str``

        :param      tag_keys: The keys of the tags associated with the
        Internet services.
        :type       tag_keys: ``list`` of ``str``

        :param      tag_values: The values of the tags associated with the
        Internet services.
        :type       tag_values: ``list`` of ``str``

        :param      tags: The key/value combination of the tags associated
        with the Internet services, in the following format:
        "Filters":{"Tags":["TAGKEY=TAGVALUE"]}.
        :type       tags: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: Returns the list of Internet Services
        :rtype: ``list`` of ``dict``
        """
        action = "ReadInternetServices"
        data = {"DryRun": dry_run, "Filters": {}}
        if internet_service_ids is not None:
            data["Filters"].update({
                "InternetServiceIds": internet_service_ids
            })
        if link_net_ids is not None:
            data["Filters"].update({"LinkNetIds": link_net_ids})
        if link_states is not None:
            data["Filters"].update({"LinkStates": link_states})
        if tag_keys is not None:
            data["Filters"].update({"TagKeys": tag_keys})
        if tag_values is not None:
            data["Filters"].update({"TagValues": tag_values})
        if tags is not None:
            data["Filters"].update({"Tags": tags})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["InternetServices"]
        return response.json()

    def ex_create_listener_rule(
        self,
        vms: [Node] = None,
        l_load_balancer_name: str = None,
        l_load_balancer_port: str = None,
        lr_action: str = None,
        lr_host_name_pattern: str = None,
        lr_id: str = None,
        lr_name: str = None,
        lr_path_pattern: str = None,
        lr_priority: int = None,
        dry_run: bool = False,
    ):
        """
        Creates a rule for traffic redirection for the specified listener.
        Each rule must have either the HostNamePattern or PathPattern parameter
        specified. Rules are treated in priority order, from the highest value
        to the lowest value.
        Once the rule is created, you need to register backend VMs with it.
        For more information, see the RegisterVmsInLoadBalancer method.
        https://docs.outscale.com/api#registervmsinloadbalancer

        :param      vms: The IDs of the backend VMs. (required)
        :type       vms: ``list`` of ``Node``

        :param      l_load_balancer_name: The name of the load balancer to
        which the listener is attached. (required)
        :type       l_load_balancer_name: ``str``

        :param      l_load_balancer_port: The port of load balancer on which
        the load balancer is listening (between 1 and 65535 both included).
        (required)
        :type       l_load_balancer_port: ``int``

        :param      lr_action: The type of action for the rule
        (always forward).
        :type       lr_action: ``str``

        :param      lr_host_name_pattern: A host-name pattern for the rule,
        with a maximum length of 128 characters. This host-name
        pattern supports maximum three wildcards, and must not contain
        any special characters except [-.?].
        :type       lr_host_name_pattern: ``str``

        :param      lr_id: The ID of the listener.
        :type       lr_id: ``str``

        :param      lr_name: A human-readable name for the listener rule.
        :type       lr_name: ``str``

        :param      lr_path_pattern: A path pattern for the rule, with a
        maximum length of 128 characters. This path pattern supports maximum
        three wildcards, and must not contain any special characters except
        [_-.$/~"'@:+?].
        :type       lr_path_pattern: ``str``

        :param      lr_priority: The priority level of the listener rule,
        between 1 and 19999 both included. Each rule must have a unique
        priority level. Otherwise, an error is returned. (required)
        :type       lr_priority: ``int``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Listener Rule
        :rtype: ``dict``
        """
        action = "CreateListenerRule"
        data = {"DryRun": dry_run, "Listener": {}, "ListenerRule": {}}

        if vms is not None:
            vm_ids = [vm.id for vm in vms]
            data.update({"VmIds": vm_ids})
        if l_load_balancer_name is not None:
            data["Listener"].update({
                "LoadBalancerName": l_load_balancer_name
            })
        if l_load_balancer_port is not None:
            data["Listener"].update({
                "LoadBalancerPort": l_load_balancer_port
            })
        if lr_action is not None:
            data["ListenerRule"].update({"Action": lr_action})
        if lr_host_name_pattern is not None:
            data["ListenerRule"].update({
                "HostNamePattern": lr_host_name_pattern
            })
        if lr_id is not None:
            data["ListenerRule"].update({"ListenerRuleId": lr_id})
        if lr_name is not None:
            data["ListenerRule"].update({"ListenerRuleName": lr_name})
        if lr_path_pattern is not None:
            data["ListenerRule"].update({"PathPattern": lr_path_pattern})
        if lr_priority is not None:
            data["ListenerRule"].update({"Priority": lr_priority})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["ListenerRule"]
        return response.json()

    def ex_create_load_balancer_listeners(
        self,
        load_balancer_name: str = None,
        l_backend_port: int = None,
        l_backend_protocol: str = None,
        l_load_balancer_port: int = None,
        l_load_balancer_protocol: str = None,
        l_server_certificate_id: str = None,
        dry_run: bool = False,
    ):
        """
        Creates one or more listeners for a specified load balancer.

        :param      load_balancer_name: The name of the load balancer for
        which you want to create listeners. (required)
        :type       load_balancer_name: ``str``

        :param      l_backend_port: The port on which the back-end VM is
        listening (between 1 and 65535, both included). (required)
        :type       l_backend_port: ``int``

        :param      l_backend_protocol: The protocol for routing traffic to
        back-end VMs (HTTP | HTTPS | TCP | SSL | UDP).
        :type       l_backend_protocol: ``int``

        :param      l_load_balancer_port: The port on which the load balancer
        is listening (between 1 and 65535, both included). (required)
        :type       l_load_balancer_port: ``int``

        :param      l_load_balancer_protocol: The routing protocol
        (HTTP | HTTPS | TCP | SSL | UDP). (required)
        :type       l_load_balancer_protocol: ``str``

        :param      l_server_certificate_id: The ID of the server certificate.
        (required)
        :type       l_server_certificate_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Load Balancer Listener
        :rtype: ``dict``
        """
        action = "CreateLoadBalancerListeners"
        data = {"DryRun": dry_run, "Listeners": {}}

        if load_balancer_name is not None:
            data.update({"LoadBalancerName": load_balancer_name})
        if l_backend_port is not None:
            data["Listeners"].update({
                "BackendPort": l_backend_port
            })
        if l_backend_protocol is not None:
            data["Listeners"].update({
                "BackendProtocol": l_backend_protocol
            })
        if l_load_balancer_port is not None:
            data["Listeners"].update({
                "LoadBalancerPort": l_load_balancer_port
            })
        if l_load_balancer_protocol is not None:
            data["Listeners"].update({
                "LoadBalancerProtocol": l_load_balancer_protocol
            })
        if l_server_certificate_id is not None:
            data["Listeners"].update({
                "ServerCertificateId": l_server_certificate_id
            })
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["LoadBalancer"]
        return response.json()

    def ex_delete_listener_rule(
        self,
        listener_rule_name: str = None,
        dry_run: bool = False,
    ):
        """
        Deletes a listener rule.
        The previously active rule is disabled after deletion.

        :param      listener_rule_name: The name of the rule you want to
        delete. (required)
        :type       listener_rule_name: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteListenerRule"
        data = {"DryRun": dry_run}
        if listener_rule_name is not None:
            data.update({"ListenerRuleName": listener_rule_name})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_delete_load_balancer_listeners(
        self,
        load_balancer_name: str = None,
        load_balancer_ports: [int] = None,
        dry_run: bool = False,
    ):
        """
        Deletes listeners of a specified load balancer.

        :param      load_balancer_name: The name of the load balancer for
        which you want to delete listeners. (required)
        :type       load_balancer_name: ``str``

        :param      load_balancer_ports: One or more port numbers of the
        listeners you want to delete.. (required)
        :type       load_balancer_ports: ``list`` of ``int``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteLoadBalancerListeners"
        data = {"DryRun": dry_run}
        if load_balancer_ports is not None:
            data.update({"LoadBalancerPorts": load_balancer_ports})
        if load_balancer_name is not None:
            data.update({"LoadBalancerName": load_balancer_name})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_list_listener_rules(
        self,
        listener_rule_names: [str] = None,
        dry_run: bool = False
    ):
        """
        Describes one or more listener rules. By default, this action returns
        the full list of listener rules for the account.

        :param      listener_rule_names: The names of the listener rules.
        :type       listener_rule_names: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: Returns the list of Listener Rules
        :rtype: ``list`` of ``dict``
        """
        action = "ReadListenerRules"
        data = {"DryRun": dry_run, "Filters": {}}
        if listener_rule_names is not None:
            data["Filters"].update({
                "ListenerRuleNames": listener_rule_names
            })
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["InternetServices"]
        return response.json()

    def ex_update_listener_rule(
        self,
        host_pattern: str = None,
        listener_rule_name: str = None,
        path_pattern: str = None,
        dry_run: bool = False,
    ):
        """
        Updates the pattern of the listener rule.
        This call updates the pattern matching algorithm for incoming traffic.

        :param      host_pattern: TA host-name pattern for the rule, with a
        maximum length of 128 characters. This host-name pattern supports
        maximum three wildcards, and must not contain any special characters
        except [-.?].
        :type       host_pattern: ``str`

        :param      listener_rule_name: The name of the listener rule.
        (required)
        :type       listener_rule_name: ``str``

        :param      path_pattern: A path pattern for the rule, with a maximum
        length of 128 characters. This path pattern supports maximum three
        wildcards, and must not contain any special characters
        except [_-.$/~"'@:+?].
        :type       path_pattern: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: Update the specified Listener Rule
        :rtype: ``dict``
        """
        action = "UpdateListenerRule"
        data = {"DryRun": dry_run}
        if host_pattern is not None:
            data.update({"HostPattern": host_pattern})
        if listener_rule_name is not None:
            data.update({"ListenerRuleName": listener_rule_name})
        if path_pattern is not None:
            data.update({"PathPattern": path_pattern})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["ListenerRule"]
        return response.json()

    def ex_create_load_balancer(
        self,
        load_balancer_name: str = None,
        load_balancer_type: str = None,
        security_groups: [str] = None,
        subnets: [str] = None,
        subregion_names: str = None,
        tag_keys: [str] = None,
        tag_values: [str] = None,
        l_backend_port: int = None,
        l_backend_protocol: str = None,
        l_load_balancer_port: int = None,
        l_load_balancer_protocol: str = None,
        l_server_certificate_id: str = None,
        dry_run: bool = False,
    ):
        """
        Creates a load balancer.
        The load balancer is created with a unique Domain Name Service (DNS)
        name. It receives the incoming traffic and routes it to its registered
        virtual machines (VMs). By default, this action creates an
        Internet-facing load balancer, resolving to public IP addresses.
        To create an internal load balancer in a Net, resolving to private IP
        addresses, use the LoadBalancerType parameter.

        :param      load_balancer_name: The name of the load balancer for
        which you want to create listeners. (required)
        :type       load_balancer_name: ``str``

        :param      load_balancer_type: The type of load balancer:
        internet-facing or internal. Use this parameter only for load
        balancers in a Net.
        :type       load_balancer_type: ``str``

        :param      security_groups: One or more IDs of security groups you
        want to assign to the load balancer.
        :type       security_groups: ``list`` of ``str``

        :param      subnets: One or more IDs of Subnets in your Net that you
        want to attach to the load balancer.
        :type       subnets: ``list`` of ``str``

        :param      subregion_names: One or more names of Subregions
        (currently, only one Subregion is supported). This parameter is not
        required if you create a load balancer in a Net. To create an internal
        load balancer, use the LoadBalancerType parameter.
        :type       subregion_names: ``list`` of ``str``

        :param      tag_keys: The key of the tag, with a minimum of 1
        character. (required)
        :type       tag_keys: ``list`` of ``str``

        :param      tag_values: The value of the tag, between 0 and 255
        characters. (required)
        :type       tag_values: ``list`` of ``str``

        :param      l_backend_port: The port on which the back-end VM is
        listening (between 1 and 65535, both included). (required)
        :type       l_backend_port: ``int``

        :param      l_backend_protocol: The protocol for routing traffic to
        back-end VMs (HTTP | HTTPS | TCP | SSL | UDP).
        :type       l_backend_protocol: ``int``

        :param      l_load_balancer_port: The port on which the load balancer
        is listening (between 1 and 65535, both included). (required)
        :type       l_load_balancer_port: ``int``

        :param      l_load_balancer_protocol: The routing protocol
        (HTTP | HTTPS | TCP | SSL | UDP). (required)
        :type       l_load_balancer_protocol: ``str``

        :param      l_server_certificate_id: The ID of the server certificate.
        (required)
        :type       l_server_certificate_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Load Balancer
        :rtype: ``dict``
        """
        action = "CreateLoadBalancer"
        data = {"DryRun": dry_run, "Listeners": {}, "Tags": {}}

        if load_balancer_name is not None:
            data.update({"LoadBalancerName": load_balancer_name})
        if load_balancer_type is not None:
            data.update({"LoadBalencerType": load_balancer_type})
        if security_groups is not None:
            data.update({"SecurityGroups": security_groups})
        if subnets is not None:
            data.update({"Subnets": subnets})
        if subregion_names is not None:
            data.update({"SubregionNames": subregion_names})
        if tag_keys and tag_values and len(tag_keys) == len(tag_values):
            for key, value in zip(tag_keys, tag_values):
                data["Tags"].update({"Key": key, "Value": value})
        if l_backend_port is not None:
            data["Listeners"].update({
                "BackendPort": l_backend_port
            })
        if l_backend_protocol is not None:
            data["Listeners"].update({
                "BackendProtocol": l_backend_protocol
            })
        if l_load_balancer_port is not None:
            data["Listeners"].update({
                "LoadBalancerPort": l_load_balancer_port
            })
        if l_load_balancer_protocol is not None:
            data["Listeners"].update({
                "LoadBalancerProtocol": l_load_balancer_protocol
            })
        if l_server_certificate_id is not None:
            data["Listeners"].update({
                "ServerCertificateId": l_server_certificate_id
            })
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["LoadBalancer"]
        return response.json()

    def ex_create_load_balancer_tags(
        self,
        load_balancer_names: [str] = None,
        tag_keys: [str] = None,
        tag_values: [str] = None,
        dry_run: bool = False,
    ):
        """
        Adds one or more tags to the specified load balancers.
        If a tag with the same key already exists for the load balancer,
        the tag value is replaced.

        :param      load_balancer_names: The name of the load balancer for
        which you want to create listeners. (required)
        :type       load_balancer_names: ``str``

        :param      tag_keys: The key of the tag, with a minimum of 1
        character. (required)
        :type       tag_keys: ``list`` of ``str``

        :param      tag_values: The value of the tag, between 0 and 255
        characters. (required)
        :type       tag_values: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Load Balancer Tags
        :rtype: ``dict``
        """
        action = "CreateLoadBalancerTags"
        data = {"DryRun": dry_run, "Tags": {}}
        if load_balancer_names is not None:
            data.update({"LoadBalancerNames": load_balancer_names})
        if tag_keys and tag_values and len(tag_keys) == len(tag_values):
            for key, value in zip(tag_keys, tag_values):
                data["Tags"].update({"Key": key, "Value": value})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["LoadBalancer"]
        return response.json()

    def ex_delete_load_balancer(
        self,
        load_balancer_name: str = None,
        dry_run: bool = False,
    ):
        """
        Deletes a specified load balancer.

        :param      load_balancer_name: The name of the load balancer you want
        to delete. (required)
        :type       load_balancer_name: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteLoadBalancer"
        data = {"DryRun": dry_run}
        if load_balancer_name is not None:
            data.update({"LoadBalancerName": load_balancer_name})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_delete_load_balancer_tags(
        self,
        load_balancer_names: [str] = None,
        tag_keys: [str] = None,
        dry_run: bool = False,
    ):
        """
        Deletes a specified load balancer tags.

        :param      load_balancer_names: The names of the load balancer for
        which you want to delete tags. (required)
        :type       load_balancer_names: ``str``

        :param      tag_keys: The key of the tag, with a minimum of
        1 character.
        :type       tag_keys: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteLoadBalancerTags"
        data = {"DryRun": dry_run, "Tags": {}}
        if load_balancer_names is not None:
            data.update({"LoadBalancerNames": load_balancer_names})
        if tag_keys is not None:
            data["Tags"].update({"Keys": tag_keys})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_deregister_vms_in_load_balancer(
        self,
        backend_vm_ids: [str] = None,
        load_balancer_name: str = None,
        dry_run: bool = False,
    ):
        """
        Deregisters a specified virtual machine (VM) from a load balancer.

        :param      backend_vm_ids: One or more IDs of back-end VMs.
        (required)
        :type       backend_vm_ids: ``str``

        :param      load_balancer_name: The name of the load balancer.
        (required)
        :type       load_balancer_name: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeregisterVmsInLoadBalancer"
        data = {"DryRun": dry_run}
        if load_balancer_name is not None:
            data.update({"LoadBalancerName": load_balancer_name})
        if backend_vm_ids is not None:
            data.update({"BackendVmIds": backend_vm_ids})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def read_load_balancer_tags(
        self,
        load_balancer_names: [str] = None,
        dry_run: bool = False,
    ):
        """
        Describes the tags associated with one or more specified load
        balancers.

        :param      load_balancer_names: The names of the load balancer.
        (required)
        :type       load_balancer_names: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: a list of load balancer tags
        :rtype: ``list`` of ``dict``
        """
        action = "ReadLoadBalancerTags"
        data = {"DryRun": dry_run}
        if load_balancer_names is not None:
            data.update({"LoadBalancerNames": load_balancer_names})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["Tags"]
        return response.json()

    def read_load_balancers(
        self,
        load_balancer_names: [str] = None,
        dry_run: bool = False,
    ):
        """
        Lists one or more load balancers and their attributes.

        :param      load_balancer_names: The names of the load balancer.
        (required)
        :type       load_balancer_names: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: a list of load balancer
        :rtype: ``list`` of ``dict``
        """
        action = "ReadLoadBalancers"
        data = {"DryRun": dry_run, "Filters": {}}
        if load_balancer_names is not None:
            data["Filters"].update({"LoadBalancerNames": load_balancer_names})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["LoadBalancers"]
        return response.json()

    def ex_list_vms_health(
        self,
        backend_vm_ids: [str] = None,
        load_balancer_name: str = None,
        dry_run: bool = False,
    ):
        """
        Lists the state of one or more back-end virtual machines (VMs)
        registered with a specified load balancer.

        :param      load_balancer_name: The name of the load balancer.
        (required)
        :type       load_balancer_name: ``str``

        :param      backend_vm_ids: One or more IDs of back-end VMs.
        :type       backend_vm_ids: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: a list of back end vms health
        :rtype: ``list`` of ``dict``
        """
        action = "ReadVmsHealth"
        data = {"DryRun": dry_run}
        if backend_vm_ids is not None:
            data.update({"BackendVmIds": backend_vm_ids})
        if load_balancer_name is not None:
            data.update({"LoadBalancerName": load_balancer_name})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["BackendVmHealth"]
        return response.json()

    def ex_register_vms_in_load_balancer(
        self,
        backend_vm_ids: [str] = None,
        load_balancer_name: str = None,
        dry_run: bool = False,
    ):
        """
        Registers one or more virtual machines (VMs) with a specified load
        balancer.
        The VMs must be running in the same network as the load balancer
        (in the public Cloud or in the same Net). It may take a little time
        for a VM to be registered with the load balancer. Once the VM is
        registered with a load balancer, it receives traffic and requests from
        this load balancer and is called a back-end VM.

        :param      load_balancer_name: The name of the load balancer.
        (required)
        :type       load_balancer_name: ``str``

        :param      backend_vm_ids: One or more IDs of back-end VMs.
        :type       backend_vm_ids: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: a list of back end vms health
        :rtype: ``list`` of ``dict``
        """
        action = "RegisterVmsInLoadBalancer"
        data = {"DryRun": dry_run, "Filters": {}}
        if backend_vm_ids is not None:
            data.update({"BackendVmIds": backend_vm_ids})
        if load_balancer_name is not None:
            data.update({"LoadBalancerName": load_balancer_name})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["BackendVmHealth"]
        return response.json()

    def ex_create_load_balancer_policy(
        self,
        cookie_name: str = None,
        load_balancer_name: str = None,
        policy_name: str = None,
        policy_type: str = None,
        dry_run: bool = False,
    ):
        """
        Creates a stickiness policy with sticky session lifetimes defined by
        the browser lifetime. The created policy can be used with HTTP or
        HTTPS listeners only.
        If this policy is implemented by a load balancer, this load balancer
        uses this cookie in all incoming requests to direct them to the
        specified back-end server virtual machine (VM). If this cookie is not
        present, the load balancer sends the request to any other server
        according to its load-balancing algorithm.

        You can also create a stickiness policy with sticky session lifetimes
        following the lifetime of an application-generated cookie.
        Unlike the other type of stickiness policy, the lifetime of the
        special Load Balancer Unit (LBU) cookie follows the lifetime of the
        application-generated cookie specified in the policy configuration.
        The load balancer inserts a new stickiness cookie only when the
        application response includes a new application cookie.
        The session stops being sticky if the application cookie is removed or
        expires, until a new application cookie is issued.

        :param      cookie_name: The name of the application cookie used for
        stickiness. This parameter is required if you create a stickiness
        policy based on an application-generated cookie.
        :type       cookie_name: ``str``

        :param      load_balancer_name: The name of the load balancer for
        which you want to create a policy. (required)
        :type       load_balancer_name: ``str``

        :param      policy_name: The name of the policy. This name must be
        unique and consist of alphanumeric characters and dashes (-).
        (required)
        :type       policy_name: ``str``

        :param      policy_type: The type of stickiness policy you want to
        create: app or load_balancer. (required)
        :type       policy_type: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Load Balancer Policy
        :rtype: ``dict``
        """
        action = "CreateLoadBalancerPolicy"
        data = {"DryRun": dry_run, "Tags": {}}
        if cookie_name is not None:
            data.update({"CookieName": cookie_name})
        if load_balancer_name is not None:
            data.update({"LoadBalancerName": load_balancer_name})
        if policy_type is not None:
            data.update({"PolicyType": policy_type})
        if policy_name is not None:
            data.update({"PolicyName": policy_name})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["LoadBalancer"]
        return response.json()

    def ex_delete_load_balancer_policy(
        self,
        load_balancer_name: str = None,
        policy_name: str = None,
        dry_run: bool = False,
    ):
        """
        Deletes a specified policy from a load balancer.
        In order to be deleted, the policy must not be enabled for any
        listener.

        :param      load_balancer_name: The name of the load balancer for
        which you want to delete a policy. (required)
        :type       load_balancer_name: ``str``

        :param      policy_name: The name of the policy you want to delete.
        (required)
        :type       policy_name: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteLoadBalancerPolicy"
        data = {"DryRun": dry_run, "Tags": {}}
        if load_balancer_name is not None:
            data.update({"LoadBalancerName": load_balancer_name})
        if policy_name is not None:
            data["Tags"].update({"PolicyName": policy_name})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_create_nat_service(
        self,
        public_ip: str = None,
        subnet_id: str = None,
        dry_run: bool = False,
    ):
        """
        Creates a network address translation (NAT) service in the specified
        public Subnet of a Net.
        A NAT service enables virtual machines (VMs) placed in the private
        Subnet of this Net to connect to the Internet, without being
        accessible from the Internet.
        When creating a NAT service, you specify the allocation ID of the
        External IP (EIP) you want to use as public IP for the NAT service.
        Once the NAT service is created, you need to create a route in the
        route table of the private Subnet, with 0.0.0.0/0 as destination and
        the ID of the NAT service as target. For more information, see
        LinkPublicIP and CreateRoute.
        This action also enables you to create multiple NAT services in the
        same Net (one per public Subnet).

        :param      public_ip: The allocation ID of the EIP to associate
        with the NAT service. (required)
        :type       public_ip: ``str``

        :param      subnet_id: The ID of the Subnet in which you want to
        create the NAT service. (required)
        :type       subnet_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Nat Service
        :rtype: ``dict``
        """
        action = "CreateNatService"
        data = {"DryRun": dry_run}
        if public_ip is not None:
            data.update({"PublicIp": public_ip})
        if subnet_id is not None:
            data.update({"SubnetId": subnet_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["NatService"]
        return response.json()

    def ex_delete_nat_service(
        self,
        nat_service_id: str = None,
        dry_run: bool = False,
    ):
        """
        Deletes a specified network address translation (NAT) service.
        This action disassociates the External IP address (EIP) from the NAT
        service, but does not release this EIP from your account. However, it
        does not delete any NAT service routes in your route tables.

        :param      nat_service_id: TThe ID of the NAT service you want to
        delete. (required)
        :type       nat_service_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteNatService"
        data = {"DryRun": dry_run}
        if nat_service_id is not None:
            data.update({"NatServiceId": nat_service_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_list_nat_services(
        self,
        nat_service_ids: [str] = None,
        net_ids: [str] = None,
        states: [str] = None,
        subnet_ids: [str] = None,
        tag_keys: [str] = None,
        tag_values: [str] = None,
        tags: [str] = None,
        dry_run: bool = False,
    ):
        """
        Lists one or more network address translation (NAT) services.

        :param      nat_service_ids: The IDs of the NAT services.
        :type       nat_service_ids: ``list`` of ``str``

        :param      net_ids: The IDs of the Nets in which the NAT services are.
        :type       net_ids: ``list`` of ``str``

        :param      states: The states of the NAT services
        (pending | available | deleting | deleted).
        :type       states: ``list`` of ``str``

        :param      subnet_ids: The IDs of the Subnets in which the NAT
        services are.
        :type       subnet_ids: ``list`` of ``str``

        :param      tag_keys: The keys of the tags associated with the NAT
        services.
        :type       tag_keys: ``list`` of ``str``

        :param      tag_values: The values of the tags associated with the NAT
        services.
        :type       tag_values: ``list`` of ``str``

        :param      tags: The values of the tags associated with the NAT
        services.
        :type       tags: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: a list of back end vms health
        :rtype: ``list`` of ``dict``
        """
        action = "ReadNatServices"
        data = {"DryRun": dry_run, "Filters": {}}
        if nat_service_ids is not None:
            data["Filters"].update({"NatServiceIds": nat_service_ids})
        if states is not None:
            data["Filters"].update({"States": states})
        if net_ids is not None:
            data["Filters"].update({"NetIds": net_ids})
        if subnet_ids is not None:
            data["Filters"].update({"SubnetIds": subnet_ids})
        if tag_keys is not None:
            data["Filters"].update({"TagKeys": tag_keys})
        if tag_values is not None:
            data["Filters"].update({"TagValues": tag_values})
        if tags is not None:
            data["Filters"].update({"Tags": tags})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["NatServices"]
        return response.json()

    def ex_create_net(
        self,
        ip_range: str = None,
        tenancy: str = None,
        dry_run: bool = False,
    ):
        """
        Creates a Net with a specified IP range.
        The IP range (network range) of your Net must be between a /28 netmask
        (16 IP addresses) and a /16 netmask (65 536 IP addresses).

        :param      ip_range: The IP range for the Net, in CIDR notation
        (for example, 10.0.0.0/16). (required)
        :type       ip_range: ``str``

        :param      tenancy: The tenancy options for the VMs (default if a VM
        created in a Net can be launched with any tenancy, dedicated if it can
        be launched with dedicated tenancy VMs running on single-tenant
        hardware).
        :type       tenancy: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Nat Service
        :rtype: ``dict``
        """
        action = "CreateNet"
        data = {"DryRun": dry_run}
        if ip_range is not None:
            data.update({"IpRange": ip_range})
        if tenancy is not None:
            data.update({"Tenancy": tenancy})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["Net"]
        return response.json()

    def ex_delete_net(
        self,
        net_id: str = None,
        dry_run: bool = False,
    ):
        """
        Deletes a specified Net.
        Before deleting the Net, you need to delete or detach all the
        resources associated with the Net:

        - Virtual machines (VMs)
        - Net peering connections
        - Custom route tables
        - External IP addresses (EIPs) allocated to resources in the Net
        - Network Interface Cards (NICs) created in the Subnets
        - Virtual gateways, Internet services and NAT services
        - Load balancers
        - Security groups
        - Subnets

        :param      net_id: The ID of the Net you want to delete. (required)
        :type       net_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteNet"
        data = {"DryRun": dry_run}
        if net_id is not None:
            data.update({"NetId": net_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_list_nets(
        self,
        dhcp_options_set_ids: [str] = None,
        ip_ranges: [str] = None,
        is_default: bool = None,
        net_ids: [str] = None,
        states: [str] = None,
        tag_keys: [str] = None,
        tag_values: [str] = None,
        tags: [str] = None,
        dry_run: bool = False,
    ):
        """
        Lists one or more Nets.

        :param      dhcp_options_set_ids: The IDs of the DHCP options sets.
        :type       dhcp_options_set_ids: ``list`` of ``str``

        :param      ip_ranges: The IP ranges for the Nets, in CIDR notation
        (for example, 10.0.0.0/16).
        :type       ip_ranges: ``list`` of ``str``

        :param      is_default: If true, the Net used is the default one.
        :type       is_default: ``bool``

        :param      net_ids: The IDs of the Nets.
        :type       net_ids: ``list`` of ``str``

        :param      states: The states of the Nets (pending | available).
        :type       states: ``list`` of ``str``

        :param      tag_keys: The keys of the tags associated with the Nets.
        :type       tag_keys: ``list`` of ``str``

        :param      tag_values: The values of the tags associated with the
        Nets.
        :type       tag_values: ``list`` of ``str``

        :param      tags: The key/value combination of the tags associated
        with the Nets, in the following format:
        "Filters":{"Tags":["TAGKEY=TAGVALUE"]}.
        :type       tags: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: A list of Nets
        :rtype: ``list`` of ``dict``
        """
        action = "ReadNets"
        data = {"DryRun": dry_run, "Filters": {}}
        if dhcp_options_set_ids is not None:
            data["Filters"].update({"DhcpOptionsSetIds": dhcp_options_set_ids})
        if ip_ranges is not None:
            data["Filters"].update({"IpRanges": ip_ranges})
        if is_default is not None:
            data["Filters"].update({"IsDefault": is_default})
        if net_ids is not None:
            data["Filters"].update({"NetIds": net_ids})
        if states is not None:
            data["Filters"].update({"States": states})
        if tag_keys is not None:
            data["Filters"].update({"TagKeys": tag_keys})
        if tag_values is not None:
            data["Filters"].update({"TagValues": tag_values})
        if tags is not None:
            data["Filters"].update({"Tags": tags})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["Nets"]
        return response.json()

    def ex_update_net(
        self,
        net_id: str = None,
        dhcp_options_set_id: str = None,
        dry_run: bool = False,
    ):
        """
        Associates a DHCP options set with a specified Net.

        :param      net_id: The ID of the Net. (required)
        :type       net_id: ``str``

        :param      dhcp_options_set_id: The ID of the DHCP options set
        (or default if you want to associate the default one). (required)
        :type       dhcp_options_set_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The modified Nat Service
        :rtype: ``dict``
        """
        action = "UpdateNet"
        data = {"DryRun": dry_run}
        if net_id is not None:
            data.update({"NetId": net_id})
        if dhcp_options_set_id is not None:
            data.update({"DhcpOptionsSetId": dhcp_options_set_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["Net"]
        return response.json()

    def ex_create_net_access_point(
        self,
        net_id: str = None,
        route_table_ids: [str] = None,
        service_name: str = None,
        dry_run: bool = False,
    ):
        """
        Creates a Net access point to access a 3DS OUTSCALE service from this
        Net without using the Internet and External IP addresses.
        You specify the service using its prefix list name. For more
        information, see DescribePrefixLists:
        https://docs.outscale.com/api#describeprefixlists
        To control the routing of traffic between the Net and the specified
        service, you can specify one or more route tables. Virtual machines
        placed in Subnets associated with the specified route table thus use
        the Net access point to access the service. When you specify a route
        table, a route is automatically added to it with the destination set
        to the prefix list ID of the service, and the target set to the ID of
        the access point.

        :param      net_id: The ID of the Net. (required)
        :type       ip_range: ``str``

        :param      route_table_ids: One or more IDs of route tables to use
        for the connection.
        :type       route_table_ids: ``list`` of ``str``

        :param      service_name: The prefix list name corresponding to the
        service (for example, com.outscale.eu-west-2.osu for OSU). (required)
        :type       service_name: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Access Net Point
        :rtype: ``dict``
        """
        action = "CreateNetAccessPoint"
        data = {"DryRun": dry_run}
        if net_id is not None:
            data.update({"NetId": net_id})
        if route_table_ids is not None:
            data.update({"RouteTableIds": route_table_ids})
        if service_name is not None:
            data.update({"ServiceName": service_name})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["NetAccessPoint"]
        return response.json()

    def ex_delete_net_access_point(
        self,
        net_access_point_id: str = None,
        dry_run: bool = False,
    ):
        """
        Deletes one or more Net access point.
        This action also deletes the corresponding routes added to the route
        tables you specified for the Net access point.

        :param      net_access_point_id: The ID of the Net access point.
        (required)
        :type       net_access_point_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteNetAccessPoint"
        data = {"DryRun": dry_run}
        if net_access_point_id is not None:
            data.update({"NetAccessPointId": net_access_point_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_list_nets_access_point_services(
        self,
        service_ids: [str] = None,
        service_names: [str] = None,
        dry_run: bool = False,
    ):
        """
        Describes 3DS OUTSCALE services available to create Net access points.
        For more information, see CreateNetAccessPoint:
        https://docs.outscale.com/api#createnetaccesspoint

        :param      service_ids: The IDs of the services.
        :type       service_ids: ``list`` of ``str``

        :param      service_names: The names of the prefix lists, which
        identify the 3DS OUTSCALE services they are associated with.
        :type       service_names: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: A list of Services
        :rtype: ``list`` of ``dict``
        """
        action = "ReadNetAccessPointsServices"
        data = {"DryRun": dry_run, "Filters": {}}
        if service_names is not None:
            data["Filters"].update({"ServiceNames": service_names})
        if service_ids is not None:
            data["Filters"].update({"ServiceIds": service_ids})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["Services"]
        return response.json()

    def ex_list_nets_access_points(
        self,
        net_access_point_ids: [str] = None,
        net_ids: [str] = None,
        service_names: [str] = None,
        states: [str] = None,
        tag_keys: [str] = None,
        tag_values: [str] = None,
        tags: [str] = None,
        dry_run: bool = False,
    ):
        """
        Describes one or more Net access points.

        :param      net_access_point_ids: The IDs of the Net access points.
        :type       net_access_point_ids: ``list`` of ``str``

        :param      net_ids: The IDs of the Nets.
        :type       net_ids: ``list`` of ``str``

        :param      service_names: The The names of the prefix lists
        corresponding to the services. For more information,
        see DescribePrefixLists:
        https://docs.outscale.com/api#describeprefixlists
        :type       service_names: ``list`` of ``str``

        :param      states: The states of the Net access points
        (pending | available | deleting | deleted).
        :type       states: ``list`` of ``str``

        :param      tag_keys: The keys of the tags associated with the Net
        access points.
        :type       tag_keys: ``list`` of ``str``

        :param      tag_values: The values of the tags associated with the
        Net access points.
        :type       tag_values: ``list`` of ``str``

        :param      tags: The key/value combination of the tags associated
        with the Net access points, in the following format:
        "Filters":{"Tags":["TAGKEY=TAGVALUE"]}.
        :type       tags: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: A list of Net Access Points
        :rtype: ``list`` of ``dict``
        """
        action = "ReadNetAccessPoints"
        data = {"DryRun": dry_run, "Filters": {}}
        if net_access_point_ids is not None:
            data["Filters"].update({"NetAccessPointIds": net_access_point_ids})
        if net_ids is not None:
            data["Filters"].update({"NetIds": net_ids})
        if service_names is not None:
            data["Filters"].update({"ServiceNames": service_names})
        if states is not None:
            data["Filters"].update({"States": states})
        if tag_keys is not None:
            data["Filters"].update({"TagKeys": tag_keys})
        if tag_values is not None:
            data["Filters"].update({"TagValues": tag_values})
        if tags is not None:
            data["Filters"].update({"Tags": tags})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["NetAccessPoints"]
        return response.json()

    def ex_update_net_access_point(
        self,
        add_route_table_ids: [str] = None,
        net_access_point_id: str = None,
        remove_route_table_ids: [str] = None,
        dry_run: bool = False,
    ):
        """
        Modifies the attributes of a Net access point.
        This action enables you to add or remove route tables associated with
        the specified Net access point.

        :param      add_route_table_ids: One or more IDs of route tables to
        associate with the specified Net access point.
        :type       add_route_table_ids: ``list`` of ``str``

        :param      net_access_point_id: The ID of the Net access point.
        (required)
        :type       net_access_point_id: ``str``

        :param      remove_route_table_ids: One or more IDs of route tables to
        disassociate from the specified Net access point.
        :type       remove_route_table_ids: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The modified Net Access Point
        :rtype: ``dict``
        """
        action = "UpdateNetAccessPoint"
        data = {"DryRun": dry_run}
        if add_route_table_ids is not None:
            data.update({"AddRouteTablesIds": add_route_table_ids})
        if net_access_point_id is not None:
            data.update({"NetAccessPointId": net_access_point_id})
        if remove_route_table_ids is not None:
            data.update({"RemoveRouteTableIds": remove_route_table_ids})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["NetAccessPoint"]
        return response.json()

    def ex_create_net_peering(
        self,
        accepter_net_id: str = None,
        source_net_id: str = None,
        dry_run: bool = False,
    ):
        """
        Requests a Net peering connection between a Net you own and a peer Net
        that belongs to you or another account.
        This action creates a Net peering connection that remains in the
        pending-acceptance state until it is accepted by the owner of the peer
        Net. If the owner of the peer Net does not accept the request within
        7 days, the state of the Net peering connection becomes expired.
        For more information, see AcceptNetPeering:
        https://docs.outscale.com/api#acceptnetpeering

        :param      accepter_net_id: The ID of the Net you want to connect
        with. (required)
        :type       accepter_net_id: ``str``

        :param      source_net_id: The ID of the Net you send the peering
        request from. (required)
        :type       source_net_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Net Peering
        :rtype: ``dict``
        """
        action = "CreateNetPeering"
        data = {"DryRun": dry_run}
        if accepter_net_id is not None:
            data.update({"AccepterNetId": accepter_net_id})
        if source_net_id is not None:
            data.update({"SourceNetId": source_net_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["NetPeering"]
        return response.json()

    def ex_accept_net_peering(
        self,
        net_peering_id: [str] = None,
        dry_run: bool = False,
    ):
        """
        Accepts a Net peering connection request.
        To accept this request, you must be the owner of the peer Net. If
        you do not accept the request within 7 days, the state of the Net
        peering connection becomes expired.

        :param      net_peering_id: The ID of the Net peering connection you
        want to accept. (required)
        :type       net_peering_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The accepted Net Peering
        :rtype: ``dict``
        """
        action = "AcceptNetPeering"
        data = {"DryRun": dry_run}
        if net_peering_id is not None:
            data.update({"NetPeeringId": net_peering_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["NetPeering"]
        return response.json()

    def ex_delete_net_peering(
        self,
        net_peering_id: [str] = None,
        dry_run: bool = False,
    ):
        """
        Deletes a Net peering connection.
        If the Net peering connection is in the active state, it can be
        deleted either by the owner of the requester Net or the owner of the
        peer Net.
        If it is in the pending-acceptance state, it can be deleted only by
        the owner of the requester Net.
        If it is in the rejected, failed, or expired states, it cannot be
        deleted.

        :param      net_peering_id: The ID of the Net peering connection you
        want to delete. (required)
        :type       net_peering_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteNetPeering"
        data = {"DryRun": dry_run}
        if net_peering_id is not None:
            data.update({"NetPeeringId": net_peering_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_list_net_peerings(
        self,
        accepter_net_account_ids: [str] = None,
        accepter_net_ip_ranges: [str] = None,
        accepter_net_net_ids: [str] = None,
        net_peering_ids: [str] = None,
        source_net_account_ids: [str] = None,
        source_net_ip_ranges: [str] = None,
        source_net_net_ids: [str] = None,
        state_messages: [str] = None,
        states_names: [str] = None,
        tag_keys: [str] = None,
        tag_values: [str] = None,
        tags: [str] = None,
        dry_run: bool = False,
    ):
        """
        Lists one or more peering connections between two Nets.

        :param      accepter_net_account_ids: The account IDs of the owners of
        the peer Nets.
        :type       accepter_net_account_ids: ``list`` of ``str``

        :param      accepter_net_ip_ranges: The IP ranges of the peer Nets, in
        CIDR notation (for example, 10.0.0.0/24).
        :type       accepter_net_ip_ranges: ``list`` of ``str``

        :param      accepter_net_net_ids: The IDs of the peer Nets.
        :type       accepter_net_net_ids: ``list`` of ``str``

        :param      source_net_account_ids: The account IDs of the owners of
        the peer Nets.
        :type       source_net_account_ids: ``list`` of ``str``

        :param      source_net_ip_ranges: The IP ranges of the peer Nets.
        :type       source_net_ip_ranges: ``list`` of ``str``

        :param      source_net_net_ids: The IDs of the peer Nets.
        :type       source_net_net_ids: ``list`` of ``str``

        :param      net_peering_ids: The IDs of the Net peering connections.
        :type       net_peering_ids: ``list`` of ``str``

        :param      state_messages: Additional information about the states of
        the Net peering connections.
        :type       state_messages: ``list`` of ``str``

        :param      states_names: The states of the Net peering connections
        (pending-acceptance | active | rejected | failed | expired | deleted).
        :type       states_names: ``list`` of ``str``

        :param      tag_keys: The keys of the tags associated with the Net
        peering connections.
        :type       tag_keys: ``list`` of ``str``

        :param      tag_values: TThe values of the tags associated with the
        Net peering connections.
        :type       tag_values: ``list`` of ``str``

        :param      tags: The key/value combination of the tags associated
        with the Net peering connections, in the following format:
        "Filters":{"Tags":["TAGKEY=TAGVALUE"]}.
        :type       tags: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: A list of Net Access Points
        :rtype: ``list`` of ``dict``
        """
        action = "ReadNetPeerings"
        data = {"DryRun": dry_run, "Filters": {}}
        if accepter_net_account_ids is not None:
            data["Filters"].update({
                "AccepterNetAccountIds": accepter_net_account_ids
            })
        if accepter_net_ip_ranges is not None:
            data["Filters"].update({
                "AccepterNetIpRanges": accepter_net_ip_ranges
            })
        if accepter_net_net_ids is not None:
            data["Filters"].update({"AccepterNetNetIds": accepter_net_net_ids})
        if source_net_account_ids is not None:
            data["Filters"].update({
                "SourceNetAccountIds": source_net_account_ids
            })
        if source_net_ip_ranges is not None:
            data["Filters"].update({
                "SourceNetIpRanges": source_net_ip_ranges
            })
        if source_net_net_ids is not None:
            data["Filters"].update({"SourceNetNetIds": source_net_net_ids})
        if net_peering_ids is not None:
            data["Filters"].update({"NetPeeringIds": net_peering_ids})
        if state_messages is not None:
            data["Filters"].update({"StateMessages": state_messages})
        if states_names is not None:
            data["Filters"].update({"StateNames": states_names})
        if tag_keys is not None:
            data["Filters"].update({"TagKeys": tag_keys})
        if tag_values is not None:
            data["Filters"].update({"TagValues": tag_values})
        if tags is not None:
            data["Filters"].update({"Tags": tags})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["NetPeerings"]
        return response.json()

    def ex_reject_net_peering(
        self,
        net_peering_id: [str] = None,
        dry_run: bool = False,
    ):
        """
        Rejects a Net peering connection request.
        The Net peering connection must be in the pending-acceptance state to
        be rejected. The rejected Net peering connection is then in the
        rejected state.

        :param      net_peering_id: The ID of the Net peering connection you
        want to reject. (required)
        :type       net_peering_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The rejected Net Peering
        :rtype: ``dict``
        """
        action = "RejectNetPeering"
        data = {"DryRun": dry_run}
        if net_peering_id is not None:
            data.update({"NetPeeringId": net_peering_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_create_nic(
        self,
        description: str = None,
        private_ips_is_primary: [str] = None,
        private_ips: [str] = None,
        security_group_ids: [str] = None,
        subnet_id: str = None,
        dry_run: bool = False,
    ):
        """
        Creates a network interface card (NIC) in the specified Subnet.

        :param      description: A description for the NIC.
        :type       description: ``str``

        :param      private_ips_is_primary: If true, the IP address is the
        primary private IP address of the NIC.
        :type       private_ips_is_primary: ``list`` of ``str``

        :param      private_ips: The private IP addresses of the NIC.
        :type       private_ips: ``list`` of ``str``

        :param      security_group_ids: One or more IDs of security groups for
        the NIC.
        :type       security_group_ids: ``list`` of ``str``

        :param      subnet_id: The ID of the Subnet in which you want to
        create the NIC. (required)
        :type       subnet_id: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Nic
        :rtype: ``dict``
        """
        action = "CreateNic"
        data = {"DryRun": dry_run, "PrivatesIps": {}}
        if description is not None:
            data.update({"Description": description})
        if security_group_ids is not None:
            data.update({"SecurityGroupIds": security_group_ids})
        if subnet_id is not None:
            data.update({"SubnetId": subnet_id})
        if private_ips is not None and private_ips_is_primary is not None:
            for primary, ip in zip(private_ips_is_primary, private_ips):
                data["PrivateIps"].update({
                    "IsPrimary": primary,
                    "PrivateIp": ip
                })
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["Nic"]
        return response.json()

    def ex_link_nic(
        self,
        nic_id: str = None,
        node: str = None,
        dry_run: bool = False,
    ):
        """
        Attaches a network interface card (NIC) to a virtual machine (VM).
        The interface and the VM must be in the same Subregion. The VM can be
        either running or stopped. The NIC must be in the available state.

        :param      nic_id: The ID of the NIC you want to delete. (required)
        :type       nic_id: ``str``

        :param      node: The node you want to attach the nic to.
        :type       nic_id: ``Node``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: a Link Id
        :rtype: ``str``
        """
        action = "LinkNic"
        data = {"DryRun": dry_run}
        if nic_id is not None:
            data.update({"NicId": nic_id})
        if node:
            data.update({"VmId": node.id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["LinkNicId"]
        return response.json()

    def ex_unlink_nic(
        self,
        link_nic_id: str = None,
        dry_run: bool = False,
    ):
        """
        Detaches a network interface card (NIC) from a virtual machine (VM).
        The primary NIC cannot be detached.

        :param      link_nic_id: The ID of the NIC you want to delete.
        (required)
        :type       link_nic_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "UnlinkNic"
        data = {"DryRun": dry_run}
        if link_nic_id is not None:
            data.update({"LinkNicId": link_nic_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_delete_nic(
        self,
        nic_id: str = None,
        dry_run: bool = False,
    ):
        """
        Deletes the specified network interface card (NIC).
        The network interface must not be attached to any virtual machine (VM).

        :param      nic_id: The ID of the NIC you want to delete. (required)
        :type       nic_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteNic"
        data = {"DryRun": dry_run}
        if nic_id is not None:
            data.update({"NicId": nic_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_link_private_ips(
        self,
        allow_relink: bool = None,
        nic_id: str = None,
        private_ips: [str] = None,
        secondary_private_ip_count: int = None,
        dry_run: bool = False,
    ):
        """
        Assigns one or more secondary private IP addresses to a specified
        network interface card (NIC). This action is only available in a Net.
        The private IP addresses to be assigned can be added individually
        using the PrivateIps parameter, or you can specify the number of
        private IP addresses to be automatically chosen within the Subnet
        range using the SecondaryPrivateIpCount parameter. You can specify
        only one of these two parameters. If none of these parameters are
        specified, a private IP address is chosen within the Subnet range.

        :param      allow_relink: If true, allows an IP address that is
        already assigned to another NIC in the same Subnet to be assigned
        to the NIC you specified.
        :type       allow_relink: ``str``

        :param      nic_id: The ID of the NIC. (required)
        :type       nic_id: ``str``

        :param      private_ips: The secondary private IP address or addresses
        you want to assign to the NIC within the IP address range of the
        Subnet.
        :type       private_ips: ``list`` of ``str``

        :param      secondary_private_ip_count: The secondary private IP a
        ddress or addresses you want to assign to the NIC within the IP
        address range of the Subnet.
        :type       secondary_private_ip_count: ``int``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return:True if the action is successful
        :rtype: ``bool``
        """
        action = "LinkPrivateIps"
        data = {"DryRun": dry_run}
        if nic_id is not None:
            data.update({"NicId": nic_id})
        if allow_relink is not None:
            data.update({"AllowRelink": allow_relink})
        if private_ips is not None:
            data.update({"PrivateIps": private_ips})
        if secondary_private_ip_count is not None:
            data.update({
                "SecondaryPrivateIpCount": secondary_private_ip_count
            })
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_list_nics(
        self,
        link_nic_sort_numbers: [int] = None,
        link_nic_vm_ids: [str] = None,
        nic_ids: [str] = None,
        private_ips_private_ips: [str] = None,
        subnet_ids: [str] = None,
        dry_run: bool = False,
    ):
        """
        Lists one or more network interface cards (NICs).
        A NIC is a virtual network interface that you can attach to a virtual
        machine (VM) in a Net.

        :param      link_nics_sort_numbers: The device numbers the NICs are
        attached to.
        :type       link_nics_sort_numbers: ``list`` of ``int``

        :param      link_nic_vm_ids: The IDs of the VMs the NICs are attached
        to.
        :type       link_nic_vm_ids: ``list`` of ``str``

        :param      nic_ids: The IDs of the NICs.
        :type       nic_ids: ``list`` of ``str``

        :param      private_ips_private_ips: The private IP addresses of the
        NICs.
        :type       private_ips_private_ips: ``list`` of ``str``

        :param      subnet_ids: The IDs of the Subnets for the NICs.
        :type       subnet_ids: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: A list of the Nics
        :rtype: ``list`` of ``dict``
        """
        action = "ReadNics"
        data = {"DryRun": dry_run, "Filters": {}}
        if link_nic_sort_numbers is not None:
            data["Filters"].update({
                "LinkNicSortNumbers": link_nic_sort_numbers
            })
        if link_nic_vm_ids is not None:
            data["Filters"].update({
                "LinkNicVmIds": link_nic_vm_ids
            })
        if nic_ids is not None:
            data["Filters"].update({"NicIds": nic_ids})
        if private_ips_private_ips is not None:
            data["Filters"].update({
                "» PrivateIpsPrivateIps": private_ips_private_ips
            })
        if subnet_ids is not None:
            data["Filters"].update({
                "SubnetIds": subnet_ids
            })
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["Nics"]
        return response.json()

    def ex_unlink_private_ips(
        self,
        nic_id: str = None,
        private_ips: [str] = None,
        dry_run: bool = False,
    ):
        """
        Unassigns one or more secondary private IPs from a network interface
        card (NIC).

        :param      nic_id: The ID of the NIC. (required)
        :type       nic_id: ``str``

        :param      private_ips: One or more secondary private IP addresses
        you want to unassign from the NIC. (required)
        :type       private_ips: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "UnlinkPrivateIps"
        data = {"DryRun": dry_run}
        if nic_id is not None:
            data.update({"NicId": nic_id})
        if private_ips is not None:
            data.update({"PrivateIps": private_ips})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_update_nic(
        self,
        description: str = None,
        link_nic_delete_on_vm_deletion: str = None,
        link_nic_id: str = None,
        security_group_ids: [str] = None,
        nic_id: str = None,
        dry_run: bool = False,
    ):
        """
        Modifies the specified network interface card (NIC). You can specify
        only one attribute at a time.

        :param      description: A new description for the NIC.
        :type       description: ``str``

        :param      link_nic_delete_on_vm_deletion: If true, the NIC is
        deleted when the VM is terminated.
        :type       link_nic_delete_on_vm_deletion: ``str``

        :param      link_nic_id: The ID of the NIC attachment.
        :type       link_nic_id: ``str``

        :param      security_group_ids: One or more IDs of security groups
        for the NIC.
        :type       security_group_ids: ``list`` of ``str``

        :param      nic_id: The ID of the NIC you want to modify. (required)
        :type       nic_id: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Nic
        :rtype: ``dict``
        """
        action = "UpdateNic"
        data = {"DryRun": dry_run, "LinkNic": {}}
        if description is not None:
            data.update({"Description": description})
        if security_group_ids is not None:
            data.update({"SecurityGroupIds": security_group_ids})
        if nic_id is not None:
            data.update({"NicId": nic_id})
        if link_nic_delete_on_vm_deletion is not None:
            data["LinkNic"].update({
                "DeleteOnVmDeletion": link_nic_delete_on_vm_deletion
            })
        if link_nic_id is not None:
            data["LinkNic"].update({
                "LinkNicId": link_nic_id
            })
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["Nic"]
        return response.json()

    def ex_list_product_types(
        self,
        product_type_ids: [str] = None,
        dry_run: bool = False,
    ):
        """
        Describes one or more product types.

        :param      product_type_ids: The IDs of the product types.
        :type       product_type_ids: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: A ``list`` of Product Type
        :rtype: ``list`` of ``dict``
        """
        action = "ReadProductTypes"
        data = {"DryRun": dry_run, "Filters": {}}
        if product_type_ids is not None:
            data["Filters"].update({
                "ProductTypeIds": product_type_ids
            })
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["ProductTypes"]
        return response.json()

    def ex_list_quotas(
        self,
        collections: [str] = None,
        quota_names: [str] = None,
        quota_types: [str] = None,
        short_descriptions: [str] = None,
        dry_run: bool = False,
    ):
        """
        Describes one or more of your quotas.

        :param      collections: The group names of the quotas.
        :type       collections: ``list`` of ``str``

        :param      quota_names: The names of the quotas.
        :type       quota_names: ``list`` of ``str``

        :param      quota_types: The resource IDs if these are
        resource-specific quotas, global if they are not.
        :type       quota_types: ``list`` of ``str``

        :param      short_descriptions: The description of the quotas.
        :type       short_descriptions: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: A ``list`` of Product Type
        :rtype: ``list`` of ``dict``
        """
        action = "ReadQuotas"
        data = {"DryRun": dry_run, "Filters": {}}
        if collections is not None:
            data["Filters"].update({
                "Collections": collections
            })
        if quota_names is not None:
            data["Filters"].update({
                "QuotaNames": quota_names
            })
        if quota_types is not None:
            data["Filters"].update({
                "QuotaTypes": quota_types
            })
        if short_descriptions is not None:
            data["Filters"].update({
                "ShortDescriptions": short_descriptions
            })
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["QuotaTypes"]
        return response.json()

    def ex_create_route(
        self,
        destination_ip_range: str = None,
        gateway_id: str = None,
        nat_service_id: str = None,
        net_peering_id: str = None,
        nic_id: str = None,
        route_table_id: str = None,
        vm_id: str = None,
        dry_run: bool = False,
    ):
        """
        Creates a route in a specified route table within a specified Net.
        You must specify one of the following elements as the target:

        - Net peering connection
        - NAT VM
        - Internet service
        - Virtual gateway
        - NAT service
        - Network interface card (NIC)

        The routing algorithm is based on the most specific match.

        :param      destination_ip_range: The IP range used for the
        destination match, in CIDR notation (for example, 10.0.0.0/24).
        (required)
        :type       destination_ip_range: ``str``

        :param      gateway_id: The ID of an Internet service or virtual
        gateway attached to your Net.
        :type       gateway_id: ``str``

        :param      nat_service_id: The ID of a NAT service.
        :type       nat_service_id: ``str``

        :param      net_peering_id: The ID of a Net peering connection.
        :type       net_peering_id: ``str``

        :param      nic_id: The ID of a NIC.
        :type       nic_id: ``str``

        :param      vm_id: The ID of a NAT VM in your Net (attached to exactly
        one NIC).
        :type       vm_id: ``str``

        :param      route_table_id: The ID of the route table for which you
        want to create a route. (required)
        :type       route_table_id: `str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Route
        :rtype: ``dict``
        """
        action = "CreateRoute"
        data = {"DryRun": dry_run}
        if destination_ip_range is not None:
            data.update({"DestinationIpRange": destination_ip_range})
        if gateway_id is not None:
            data.update({"GatewayId": gateway_id})
        if nat_service_id is not None:
            data.update({"NatServiceId": nat_service_id})
        if net_peering_id is not None:
            data.update({"NetPeeringId": net_peering_id})
        if nic_id is not None:
            data.update({"NicId": nic_id})
        if route_table_id is not None:
            data.update({"RouteTableId": route_table_id})
        if vm_id is not None:
            data.update({"VmId": vm_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["RouteTable"]
        return response.json()

    def ex_delete_route(
        self,
        destination_ip_range: str = None,
        route_table_id: str = None,
        dry_run: bool = False,
    ):
        """
        Deletes a route from a specified route table.

        :param      destination_ip_range: The exact IP range for the route.
        (required)
        :type       destination_ip_range: ``str``

        :param      route_table_id: The ID of the route table from which you
        want to delete a route. (required)
        :type       route_table_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteRoute"
        data = {"DryRun": dry_run}
        if destination_ip_range is not None:
            data.update({"DestinationIpRange": destination_ip_range})
        if route_table_id is not None:
            data.update({"RouteTableId": route_table_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_update_route(
        self,
        destination_ip_range: str = None,
        gateway_id: str = None,
        nat_service_id: str = None,
        net_peering_id: str = None,
        nic_id: str = None,
        route_table_id: str = None,
        vm_id: str = None,
        dry_run: bool = False,
    ):
        """
        Replaces an existing route within a route table in a Net.
        You must specify one of the following elements as the target:

        - Net peering connection
        - NAT virtual machine (VM)
        - Internet service
        - Virtual gateway
        - NAT service
        - Network interface card (NIC)

        The routing algorithm is based on the most specific match.

        :param      destination_ip_range: The IP range used for the
        destination match, in CIDR notation (for example, 10.0.0.0/24).
        (required)
        :type       destination_ip_range: ``str``

        :param      gateway_id: The ID of an Internet service or virtual
        gateway attached to your Net.
        :type       gateway_id: ``str``

        :param      nat_service_id: The ID of a NAT service.
        :type       nat_service_id: ``str``

        :param      net_peering_id: The ID of a Net peering connection.
        :type       net_peering_id: ``str``

        :param      nic_id: The ID of a NIC.
        :type       nic_id: ``str``

        :param      vm_id: The ID of a NAT VM in your Net (attached to exactly
        one NIC).
        :type       vm_id: ``str``

        :param      route_table_id: The ID of the route table for which you
        want to create a route. (required)
        :type       route_table_id: `str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The updated Route
        :rtype: ``dict``
        """
        action = "UpdateRoute"
        data = {"DryRun": dry_run}
        if destination_ip_range is not None:
            data.update({"DestinationIpRange": destination_ip_range})
        if gateway_id is not None:
            data.update({"GatewayId": gateway_id})
        if nat_service_id is not None:
            data.update({"NatServiceId": nat_service_id})
        if net_peering_id is not None:
            data.update({"NetPeeringId": net_peering_id})
        if nic_id is not None:
            data.update({"NicId": nic_id})
        if route_table_id is not None:
            data.update({"RouteTableId": route_table_id})
        if vm_id is not None:
            data.update({"VmId": vm_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["RouteTable"]
        return response.json()

    def ex_create_route_table(
        self,
        net_id: str = None,
        dry_run: bool = False,
    ):
        """
        Creates a route table for a specified Net.
        You can then add routes and associate this route table with a Subnet.

        :param      net_id: The ID of the Net for which you want to create a
        route table.
        (required)
        :type       net_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: The new Route Table
        :rtype: ``dict``
        """
        action = "CreateRouteTable"
        data = {"DryRun": dry_run}
        if net_id is not None:
            data.update({"NetId": net_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["RouteTable"]
        return response.json()

    def ex_delete_route_table(
        self,
        route_table_id: str = None,
        dry_run: bool = False,
    ):
        """
        Deletes a specified route table.
        Before deleting a route table, you must disassociate it from any
        Subnet. You cannot delete the main route table.

        :param      route_table_id: The ID of the route table you want to
        delete. (required)
        :type       route_table_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "DeleteRouteTable"
        data = {"DryRun": dry_run}
        if route_table_id is not None:
            data.update({"RouteTableId": route_table_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def ex_link_route_table(
        self,
        route_table_id: str = None,
        subnet_id: str = None,
        dry_run: bool = False,
    ):
        """
        Associates a Subnet with a route table.
        The Subnet and the route table must be in the same Net. The traffic is
        routed according to the route table defined within this Net. You can
        associate a route table with several Subnets.

        :param      route_table_id: The ID of the route table. (required)
        :type       route_table_id: ``str``

        :param      subnet_id: The ID of the Subnet. (required)
        :type       subnet_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: Link Route Table Id
        :rtype: ``str``
        """
        action = "LinkRouteTable"
        data = {"DryRun": dry_run}
        if route_table_id is not None:
            data.update({"RouteTableId": route_table_id})
        if subnet_id is not None:
            data.update({"SubnetId": subnet_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["LinkRouteTableId"]
        return response.json()

    def ex_list_route_table(
        self,
        link_route_table_ids: [str] = None,
        link_route_table_link_route_table_ids: [str] = None,
        link_route_table_main: bool = None,
        link_subnet_ids: [str] = None,
        net_ids: [str] = None,
        route_creation_methods: [str] = None,
        route_destination_ip_ranges: [str] = None,
        route_destination_service_ids: [str] = None,
        route_gateway_ids: [str] = None,
        route_nat_service_ids: [str] = None,
        route_net_peering_ids: [str] = None,
        route_states: [str] = None,
        route_table_ids: [str] = None,
        route_vm_ids: [str] = None,
        tag_keys: [str] = None,
        tag_values: [str] = None,
        tags: [str] = None,
        dry_run: bool = False,
    ):
        """
        Lists one or more of your route tables.
        In your Net, each Subnet must be associated with a route table. If a
        Subnet is not explicitly associated with a route table, it is
        implicitly associated with the main route table of the Net.

        :param      link_route_table_ids: The IDs of the route tables involved
        in the associations.
        :type       link_route_table_ids: ``list`` of ``str``

        :param      link_route_table_link_route_table_ids: The IDs of the
        associations between the route tables and the Subnets.
        :type       link_route_table_link_route_table_ids: ``list`` of ``str``

        :param      link_route_table_main: If true, the route tables are the
        main ones for their Nets.
        :type       link_route_table_main: ``bool``

        :param      link_subnet_ids: The IDs of the Subnets involved in the
        associations.
        :type       link_subnet_ids: ``list`` of ``str``

        :param      net_ids: The IDs of the route tables involved
        in the associations.
        :type       net_ids: ``list`` of ``str``

        :param      route_creation_methods: The methods used to create a route.
        :type       route_creation_methods: ``list`` of ``str``

        :param      route_destination_ip_ranges: The IP ranges specified in
        routes in the tables.
        :type       route_destination_ip_ranges: ``list`` of ``str``

        :param      route_destination_service_ids: The service IDs specified
        in routes in the tables.
        :type       route_destination_service_ids: ``list`` of ``str``

        :param      route_gateway_ids: The IDs of the gateways specified in
        routes in the tables.
        :type       route_gateway_ids: ``list`` of ``str``

        :param      route_nat_service_ids: The IDs of the NAT services
        specified in routes in the tables.
        :type       route_nat_service_ids: ``list`` of ``str``

        :param      route_net_peering_ids: The IDs of the Net peering
        connections specified in routes in the tables.
        :type       route_net_peering_ids: ``list`` of ``str``

        :param      route_states: The states of routes in the route tables
        (active | blackhole). The blackhole state indicates that the target
        of the route is not available.
        :type       route_states: ``list`` of ``str``

        :param      route_table_ids: The IDs of the route tables.
        :type       route_table_ids: ``list`` of ``str``

        :param      route_vm_ids: The IDs of the VMs specified in routes in
        the tables.
        :type       route_vm_ids: ``list`` of ``str``

        :param      tag_keys: The keys of the tags associated with the route
        tables.
        :type       tag_keys: ``list`` of ``str``

        :param      tag_values: The values of the tags associated with the
        route tables.
        :type       tag_values: ``list`` of ``str``

        :param      tags: The key/value combination of the tags associated
        with the route tables, in the following format:
        "Filters":{"Tags":["TAGKEY=TAGVALUE"]}.
        :type       tags: ``list`` of ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: list of Route Tables
        :rtype: ``list`` of ``dict``
        """
        action = "ReadRouteTables"
        data = {"DryRun": dry_run, "Filters": {}}
        if link_route_table_ids is not None:
            data["Filters"].update({
                "LinkRouteTableIds": link_route_table_ids
            })
        if link_route_table_link_route_table_ids is not None:
            data["Filters"].update({
                "LinkRouteTableLinkRouteTableIds":
                link_route_table_link_route_table_ids
            })
        if link_route_table_main is not None:
            data["Filters"].update({
                "LinkRouteTableMain": link_route_table_main
            })
        if link_subnet_ids is not None:
            data["Filters"].update({
                "LinkSubnetIds": link_subnet_ids
            })
        if net_ids is not None:
            data["Filters"].update({
                "NetIds": net_ids
            })
        if route_creation_methods is not None:
            data["Filters"].update({
                "RouteCreationMethods": route_creation_methods
            })
        if route_destination_ip_ranges is not None:
            data["Filters"].update({
                "RouteDestinationIpRanges": route_destination_ip_ranges
            })
        if route_destination_service_ids is not None:
            data["Filters"].update({
                "RouteDestinationServiceIds": route_destination_service_ids
            })
        if route_gateway_ids is not None:
            data["Filters"].update({
                "RouteGatewayIds": route_gateway_ids
            })
        if route_nat_service_ids is not None:
            data["Filters"].update({
                "RouteNatServiceIds": route_nat_service_ids
            })
        if route_net_peering_ids is not None:
            data["Filters"].update({
                "RouteNetPeeringIds": route_net_peering_ids
            })
        if route_states is not None:
            data["Filters"].update({
                "RouteStates": route_states
            })
        if route_table_ids is not None:
            data["Filters"].update({
                "RouteTableIds": route_table_ids
            })
        if route_vm_ids is not None:
            data["Filters"].update({
                "RouteVmIds": route_vm_ids
            })
        if tag_keys is not None:
            data["Filters"].update({
                "TagKeys": tag_keys
            })
        if tag_values is not None:
            data["Filters"].update({
                "TagValues": tag_values
            })
        if tags is not None:
            data["Filters"].update({
                "Tags": tags
            })
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return response.json()["RouteTables"]
        return response.json()

    def ex_unlink_route_table(
        self,
        link_route_table_id: str = None,
        dry_run: bool = False,
    ):
        """
        Disassociates a Subnet from a route table.
        After disassociation, the Subnet can no longer use the routes in this
        route table, but uses the routes in the main route table of the Net
        instead.

        :param      link_route_table_id: The ID of the route table. (required)
        :type       link_route_table_id: ``str``

        :param      dry_run: If true, checks whether you have the required
        permissions to perform the action.
        :type       dry_run: ``bool``

        :return: True if the action is successful
        :rtype: ``bool``
        """
        action = "UnlinkRouteTable"
        data = {"DryRun": dry_run}
        if link_route_table_id is not None:
            data.update({"LinkRouteTableId": link_route_table_id})
        response = self._call_api(action, json.dumps(data))
        if response.status_code == 200:
            return True
        return False

    def _get_outscale_endpoint(self, region: str, version: str, action: str):
        return "https://api.{}.{}/api/{}/{}".format(
            region,
            self.base_uri,
            version,
            action
        )

    def _call_api(self, action: str, data: str):
        headers = self._ex_generate_headers(action, data)
        endpoint = self._get_outscale_endpoint(self.region,
                                               self.version,
                                               action)
        return requests.post(endpoint, data=data, headers=headers)

    def _ex_generate_headers(self, action: str, data: str):
        return self.signer.get_request_headers(
            action=action,
            data=data,
            service_name=self.service_name,
            region=self.region
        )

    def _to_location(self, location):
        country = location["Name"].split(", ")[1]
        return NodeLocation(
            id=location["Code"],
            name=location["Name"],
            country=country,
            driver=self,
            extra=location
        )

    def _to_locations(self, locations: list):
        return [self._to_location(location) for location in locations]

    def _to_snapshot(self, snapshot):
        name = None
        for tag in snapshot["Tags"]:
            if tag["Key"] == "Name":
                name = tag["Value"]
        return VolumeSnapshot(
            id=snapshot["SnapshotId"],
            name=name,
            size=snapshot["VolumeSize"],
            driver=self,
            state=snapshot["State"],
            created=None,
            extra=snapshot
        )

    def _to_snapshots(self, snapshots):
        return [self._to_snapshot(snapshot) for snapshot in snapshots]

    def _to_volume(self, volume):
        name = ""
        for tag in volume["Tags"]:
            if tag["Key"] == "Name":
                name = tag["Value"]
        return StorageVolume(
            id=volume["VolumeId"],
            name=name,
            size=volume["Size"],
            driver=self,
            state=volume["State"],
            extra=volume
        )

    def _to_volumes(self, volumes):
        return [self._to_volumes(volume) for volume in volumes]

    def _to_node(self, vm):
        name = ""
        private_ips = []
        for tag in vm["Tags"]:
            if tag["Key"] == "Name":
                name = tag["Value"]
        if "Nics" in vm:
            private_ips = vm["Nics"]["PrivateIps"]

        return Node(id=vm["VmId"],
                    name=name,
                    state=self.NODE_STATE[vm["State"]],
                    public_ips=[],
                    private_ips=private_ips,
                    driver=self,
                    extra=vm)

    def _to_nodes(self, vms: list):
        return [self._to_node(vm) for vm in vms]

    def _to_node_image(self, image):
        name = ""
        for tag in image["Tags"]:
            if tag["Key"] == "Name":
                name = tag["Value"]
        return NodeImage(id=image["NodeId"],
                         name=name,
                         driver=self,
                         extra=image)

    def _to_node_images(self, node_images: list):
        return [self._to_node_image(node_image) for node_image in node_images]

    def _to_key_pairs(self, key_pairs):
        return [self._to_key_pair(key_pair) for key_pair in key_pairs]

    def _to_key_pair(self, key_pair):
        private_key = ""
        if "PrivateKey" in key_pair:
            private_key = key_pair["PrivateKey"]
        return KeyPair(
            name=key_pair["KeypairName"],
            public_key="",
            private_key=private_key,
            fingerprint=key_pair["KeypairFingerprint"],
            driver=self)
