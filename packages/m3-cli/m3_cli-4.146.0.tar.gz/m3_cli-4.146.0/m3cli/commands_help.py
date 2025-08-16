describe_instances = """
Describes instances existing in a specific region for a specific tenant

Examples:

1. Describe all instances belonging to the tenant in a specific region:
        m3 describe-instances --region <region> --tenant <tenant>

2. Describe instances with a specific tag:
        m3 describe-instances --region <region> --tenant <tenant> --resource-tag <key:value>

3. Describe instances with provided owner:
        m3 describe-instances --region <region> --tenant <tenant> --owner <owner>
"""

create_image = """
Creates an image based on an existing instance

Example:
        m3 create-image --name <image_name> --instance-id <instance_id> --region <region> --tenant <tenant_name> --description <"new image description">
"""

add_schedule_instances = """
Adds an existing schedule to one or several  instances

Examples:

1.  Adds a schedule for a single instance:
        m3 add-schedule-instances --cloud <cloud> --region <region> --tenant <tenant_name> --instance-id <instance_id>,<instance_idN> -dn <schedule_name>

2. Adds a schedule for multiple instances:
        m3 add-schedule-instances --cloud <cloud> --region <region> --tenant <tenant_name> --instance-id <instance_id>,<instance_idN> -dn <schedule_name>
"""

create_instance_quota = """
Sets up a number of instances allowed for creation on a specific tenant within a specific interval

Example:
        m3 create-instance-quota --tenant <tenant_name> --region <region_name> --instance-amount <instances_number> --creation-interval-hours <hours>
"""

create_key = """
Creates a SSH key used to access instances without need to provide login credentials

Example:
       m3 create-key --key-name <key_name> --cloud <cloud> --region <region> --tenant <tenant_name>
"""

create_schedule = """
Creates a new schedule for automatic instance state management

Examples:

1. Creates a new schedule to start or stop explicit instances:
        m3 create-schedule --action <action> --cloud <cloud> --region <region> --cron <"cron expression"> --description <"schedule description"> --name <name> --schedule-type <"schedule type"> --instance-id <instance_id> --tenant <tenant_name>

2. Creates a new schedule to start or stop instances with tag:
        m3 create-schedule --action <action> --cloud <cloud> --region <region> --cron <"cron expression"> --description <"schedule description"> --name <name> --schedule-type <"schedule type"> --tenant <tenant_name> --tag-key <key> --tag-value <value>
"""

create_storage_quota = """
Sets up an amount and size of storages allowed for creation on a specific tenant within a specific interval

Example:
        m3 create-storage-quota --tenant <tenant_name> --region <region_name> --storage-amount <storage_number> --creation-interval-hours <hours> --storage-max-size <size_GB>
"""

delete_image = """
Deletes an image created from a project instance

Example:
        m3 delete-image --image-id <image_id> --region <region> --tenant <tenant_name>
"""

delete_instance_quota = """
Deletes the limitation for the number of instances allowed for creation on a specific tenant within a specific interval

Example:
        m3 delete-instance-quota --tenant <tenant_name> --region <region_name>
"""

delete_key = """
Deletes a SSH key from your account

Example:
        m3 delete-key --key-name <key_name>
"""

delete_tags = """
Deletes one or several tags from an instance in public or private cloud

Examples:
      
1. Updates instance tags:
        m3 delete-tags --cloud <cloud_name> --instance-id <instance_id> --tenant <tenant_name> --region <region_name> --tag <tag_names>

2. Updates instance tags in a public cloud (Google) in a specific availability zone:
        m3 delete-tags --cloud <cloud_name> --instance-id <instance_id> --tenant <tenant_name> --region <region_name> --tag <tag_names> --availability-zone <zone_name>

3. Updates instance tags in a public cloud (Azure) in a specific resource group:
        m3 delete-tags --cloud <cloud_name> --instance-id <instance_id> --tenant <tenant_name> --region <region_name> --tag <tag_names> --resource-group <resource_group_name>
"""

delete_schedule = """
Deletes a schedule from your tenants schedule library

Example:
        m3 delete-schedule --region <region> --name <name> --tenant <tenant_name>
"""

delete_schedule_instances = """
Deletes a schedule from one or several  instances

Example:
        m3 delete-schedule-instances --cloud <cloud> --region<region> --instance-id <instance_id1>,<instance_idN> -dn <schedule_name> --tenant <tenant_name>
"""

delete_scripts = """
Deletes an init script from your library in Maestro

Example:
        m3 delete-scripts --cloud <cloud_name> --file <file_name> --tenant <tenant_name>
"""

delete_storage_quota = """
Deletes the limitations for an amount and size of storages allowed for creation on a specific tenant within a specific interval

Example:
        m3 delete-storage-quota  --tenant <tenant_name> --region <region_name>
"""

describe_events = """
Lists the events that took place in your virtual infrastructure

Examples:

1. Describes all events in a specific tenant:
         m3 describe-events --tenant <tenant_name> --cloud <cloud> --number-of-events <number> --search-type <type>

2. Describes events related to a specific resource:
         m3 describe-events --tenant <tenant_name> --cloud <cloud> --number-of-events <number> --search-type <type> --resource-id <resource> --region <region>
"""

describe_images = """
Describes images available in a specific region for a specific tenant

Example:
        m3 describe-images --region <region> --tenant <tenant>
"""

describe_keys = """
Describes your SSH keys existing for a specific tenant

Examples:

1. Describe all keypairs belonging to the tenant:
        m3 describe-keys --region <region> --tenant <tenant>

2. Describe keypairs applied in a specific cloud and region:
        m3 describe-keys --cloud <cloud> --region <region> --tenant <tenant>
"""

deactivate_platform_service = """
Deactivates a platform service running for your tenant

Example:
        m3 deactivate-platform-service --cloud <cloud> --region <region> --tenant <tenant_name> --service-id <service_id>
"""

activate_platform_service = """
Activates a platform service for your tenant

Examples:

1. Activate a specific service without additional parameters:
        m3 activate-platform-service --cloud <cloud> --region <region> --tenant <tenant_name> --service <service_name>
"""

generate_platform_service_varfile = """
"Generates a file with variables for the specified platform service, or fills it with missing parameters if the file already exists. 
The template is prefilled with default values if available"

Example:
        m3 generate-platform-service-varfile --cloud <cloud> --region <region> --tenant <tenant_name> --service <service_name>
"""

update_platform_service = """
Updates specified elements of the platform service

Example:
        m3 update-platform-service --service<name>
"""

add_service_section = """
Adds usage/support section to the certain published service

Example:
        m3 add-service-section --service <name> --section <section_name> --block-title <title> --block-value <value>
"""

delete_platform_service = """
Removes the specified service from the catalog

Example:
        m3 delete-platform-service --service <name>
"""


publish_platform_service = """
Publishes a new service based on the specified template to the catalog

Example:
        m3 publish-platform-service --service <name> --delivery-method <delivery_method> --operating-system <os_name> --service-version <version> 
                           --template <name> --discoverable-url <dis_url> --title <title> --supported-cloud <cloud1,cloudN>
                           --icon-path <path> --cloud <cloud> --tenant 
                           <tenant_name> --all-tenants
"""

describe_platform_services = """
Provides details about the configuration of platform services:

Examples:
1.	Provides details about platform services available in a tenant:
        m3 describe-platform-services --tenant <tenant_name> --cloud <cloud> --template-type <template_type>

2.	Provides details about a platform service:
        m3 describe-platform-services --service <service_name> --json 
"""

describe_platform_service_stacks = """
Provides details about platform service stacks activated for a customer

Examples:
1.	Provides details about platform service stacks activated in all tenants:
        m3 describe-platform-service-stacks --cloud <cloud> --tenant <tenant_name> --region <region_name> --service <service_name> --all

2.	Provides details about a platform services stack available in a tenant:
        m3 describe-platform-service-stacks --cloud <cloud> --tenant <tenant_name> --region <region_name> --service <service_name>
        
3.	Provides details about platform services stack by service-id:
        m3 describe-platform-service-stacks --cloud <cloud> --tenant <tenant_name> --region <region_name> --service-id <service_id>
"""

describe_tags = """
Describes tags on an instance in public or private cloud

Examples:
    
1. Describes instance tags:
    m3 describe-tags --cloud <cloud_name> --instance-id <instance_id> --tenant <tenant_name> --region <region_name> 
    
2. Describes instance tags in a public cloud (Google) in a specific availability zone:
    m3 describe-tags --cloud <cloud_name> --instance-id <instance_id> --tenant <tenant_name> --region <region_name> --availability-zone <zone_name>

3. Describes instance tags in a public cloud (Azure) in a specific resource group:
    m3 describe-tags --cloud <cloud_name> --instance-id <instance_id> --tenant <tenant_name> --region <region_name> --resource-group <resource_group_name>
"""

describe_regions = """
Describes the regions available for a tenant in the specified cloud

Example:
        m3 describe-regions --instance-id <instance_id> --tenant <tenant_name> --region <region_name> 
"""

describe_schedules = """
Describes the schedules set to instances in your tenant

Examples:

1. Describes schedules within a specific cloud and region:
        m3 describe-schedules --cloud <cloud> --tenant <tenant_name> --region <region_name>

2. Describe schedules applied for a specific instance: 
        m3 describe-schedules --cloud <cloud> --tenant <tenant_name> --region <region_name> --instance-id <instance_id>
"""

describe_script = """
Describes the script files uploaded to Maestro and available for your tenant 

Examples:

1. Describes all available script files:
        m3 describe-script --cloud <cloud> --tenant <tenant_name> 

2. Provides the content of the specific file: 
        m3 describe-script --cloud <cloud> --tenant <tenant_name> --script <script_name>
"""

describe_shapes = """
Describes the shapes available for your tenant

Example:
        m3 describe-shapes --cloud <cloud> --tenant <tenant_name> --region <region>
"""

describe_tenants = """
Describes the tenants available for the user

Examples:

1. Outputs the list of all tenants in the cloud:
        m3 describe-tenants --cloud <cloud_name>  

2. Outputs the list of inactive tenants in the cloud:
        m3 describe-tenants --cloud <cloud_name> --inactive

3. Outputs the description of particular tenants:
        m3 describe-tenants --cloud <cloud_name> --tenant-list <tenant_name1>,<tenant_nameN> 
"""

describe_storages = """
Describes instance storages existing in the specific tenant

Examples:

1. Describes all storages on the user's tenant and region: 
        m3 describe-storages --region <region_name> --tenant <name>

2. Describes the storages on a specified instance:
        m3 describe-storages --region <region_name> --tenant <name> --instance-id <instance_id>

3. Describes the specific storage:
        m3 describe-storages --region <region_name> --tenant <name> --storage-id <storage_id1>,<storage_idN>
"""

describe_instance_quota = """
Describes the limitation for the number of instances allowed for creation on a specific tenant within a specific interval

Example:
        m3 describe-instance-quota --region <region_name> --tenant <name>
"""

describe_storage_quota = """
Describes the limitation for the number and size of storages allowed for creation on a specific tenant within a specific interval

Example:
        m3 describe-storage-quota --region <region_name> --tenant <name>
"""

health_check = """
Describes system status

Example:
        m3 health-check 
"""

hourly_report = """
Gets hourly billing report for the specified tenant

Example:
        1. Specify year, month and day:
        m3 hourly-report --year <yyyy> --month <mm> --day <dd> --tenant-group <tenant_group_name>

        2. Specify date:
        m3 hourly-report --date <date> --tenant-group <tenant_group_name>

Note: Use either 'year', 'month', and 'day', OR 'date'
"""

import_key = """
Imports SSH keys for a specific cloud, region and tenant to Maestro

Example:
        m3 import-key --file-path <path> --key-name <keypair name> --cloud <cloud_name> --region <region_name> --tenant <tenant_name>
"""

price = """
Describes the pricing policy

Example:
        m3 price --policy-type <policy> --zone-name <zone_name> --from <dd.mm.yyyy> --to <dd.mm.yyyy> 
"""

reboot_instances = """
Reboots the specified virtual instance

Example:
        m3 reboot-instances --instance-id <instance_id> --region <region_name> --tenant <tenant_name> 
"""

resource_report = """
Gets resource billing report for the specified tenant

Examples:
    1. For the current month (specify year and month):
       m3 resource-report --tenant-group <tenant_group_name> --year <yyyy> --month <mm>

    2. For a specific day (specify year, month, and day):
       m3 resource-report --tenant-group <tenant_group_name> --year <yyyy> --month <mm> --day <dd>

    3. For a date range (from - to):
       m3 resource-report --tenant-group <tenant_group_name> --from <dd.mm.yyyy> --to <dd.mm.yyyy>

Note: Use either 'year' and 'month' (and optionally 'day'), OR 'from' and 'to'
"""

run_instances = """
Creates instances of the specified configuration

Examples:

1. Runs a single instance:
        m3 run-instances --image <image_name> ---name <instance_name> --key-name <key_name> --number-of-instances <number> --cloud <cloud> --tenant <tenant_name> --region <region_name> --shape <shape_name> --script <script_name> --tag <tag_key1:val1,tag_key2:val2>

2. Runs several instances from one image:
        m3 run-instances --image <image_nam> --name <instance_name> --key-name <key_name> --number-of-instances <number> --cloud <cloud> --tenant <tenant_name> --region <region_name> --shape <shape_name> --script <script_name> --tag <tag_key1:val1,tag_key2:val2>
"""

set_tags = """
Updates instance tags. Applicable in public and private clouds

Examples:

1. Updates instance tags:
        m3 set-tags --cloud <cloud_name> --instance-id <instance_id> --tenant <tenant_name> --region <region_name> --tag <tag_names>

2. Updates instance tags in a public cloud (Google) in a specific availability zone:
        m3 set-tags --cloud <cloud_name> --instance-id <instance_id> --tenant <tenant_name> --region <region_name> --tag <tag_names> --availability-zone <zone_name>

3. Updates instance tags in a public cloud (Azure) in a specific resource group:
        m3 set-tags --cloud <cloud_name> --instance-id <instance_id> --tenant <tenant_name> --region <region_name> --tag <tag_names> --resource-group <resource_group_name>
        
4. Updates tag for the instance with a specified storage (only for private cloud):
        m3 set-tags --cloud <cloud_name> --instance-id <instance_id> --tenant <tenant_name> --region <region_name> --tag <tag_names> --storage-id <storage_id1>,<storage_idN>
"""

start_instances = """
Starts a virtual instance that has been previously stopped

Example:
        m3 start-instances --instance-id <instance_id> --tenant <tenant_name> --region <region_name>
"""

stop_instances = """
Stops a virtual instance

Example:
        m3 stop-instances --instance-id <instance_id> --tenant <tenant_name> --region <region_name>
"""

subtotal_report = """
Gets subtotal billing report for the specified tenant

Examples:
    1. For the current month (specify year and month):
        m3 subtotal-report --tenant-group <tenant_group_name> --year <yyyy> --month <mm>

    2. For a specific day (specify year, month, and day):
        m3 subtotal-report --tenant-group <tenant_group_name> --year <yyyy> --month <mm> --day <dd>

    3. For a date range (from - to):
        m3 subtotal-report --tenant-group <tenant_group_name> --from <dd.mm.yyyy> --to <dd.mm.yyyy>

    4. Show only adjustments:
        m3 subtotal-report --tenant-group <tenant_group_name> --year <yyyy> --month <mm> --day <dd> --adjustment

Note: Use either 'year' and 'month' (and optionally 'day'), OR 'from' and 'to'
"""


budgets_report = """
Gets budgets billing report for the specified tenant

Examples:
        m3 budgets-report --tenant-group <tenant_group_name> --year <yyyy> --month <mm>
"""


terminate_instances = """
Terminates a virtual instance

Example:
        m3 terminate-instances --instance-id <instance_id> --region <region_name> --tenant <tenant_name>   
"""

upload_terraform_template = """
Uploads a Terraform template

Examples:
        m3 upload-terraform-template --source-path <path> --terraform-version <version> --cloud <cloud> --tenant <tenant_name> --template <name> 
                                    --variables "key1:\\\"value1_1,value1_2\\\",key2:value2,key3:\\\"key3_1=value3_1\\\"" OR --variables-file <path_to_file>
"""
export_terraform_template = """
Exports a Terraform template as a signed URL

Example:
        m3 export-terraform-template --cloud <cloud> --tenant <tenant_name> --template <name>
"""
describe_terraform_stacks = """
Describes a Terraform stack

Example:
        m3 describe-terraform-stacks --cloud <cloud> --tenant <tenant_name> --stack-id <stack_id1>,<stack_idN>
"""

apply_terraform_template = """
Applies a Terraform template

Examples:

1. Applies a Terraform template:
        m3 apply-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name>   

2. Applies a Terraform template with specific parameters for a string:
        m3 apply-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name> --variable <key:value> 

3. Applies a Terraform template with specific parameters for a list:
        m3 apply-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name> --variable <key:"value1, valueN"> 

4. Applies a Terraform template with specific parameters for an object:
        m3 apply-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name> --variable <key1:"key2=value2"> 

5. Applies a Terraform template with multiple values, which can be a combination of strings, lists, and objects:
        m3 apply-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name> --variables "key1:\\\"value1_1,value1_2\\\",key2:value2,key3:\\\"key3_1=value3_1\\\""

6. Applies a Terraform template with specific values in a JSON file. Supported types: STRING, LIST, MAP, NUMBER, BOOL:
        m3 apply-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name> --variables-file <path_to_file>
"""

lock_terraform_template = """
Lock a Terraform template to prevent any actions from other users

Example:
    m3 lock-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name> --expiration <hours>
"""

prolong_terraform_template_lock = """
Prolong a Terraform template lock to prevent any actions from other users

Example:
    m3 prolong-terraform-template-lock --cloud <cloud_name> --template <name> --tenant <tenant_name> --expiration <hours>
"""

unlock_terraform_template = """
Unlock a Terraform template to allow actions from other users

Example:
    m3 unlock-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name> --expiration <hours>
"""

delete_terraform_template = """
Deletes a Terraform template

Example:
    m3 delete-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name>  
"""

describe_terraform_templates = """
Describes Terraform and AWS_CLOUD_FORMATION templates general info

Examples:

1. Describes Terraform templates existing on the tenant:
        m3 describe-terraform-templates --cloud <cloud_name> --tenant <tenant_name>

2. Describes listed Terraform templates on the tenant:
        m3 describe-terraform-templates --cloud <cloud_name> --tenant <tenant_name> --template <name1>,<nameN> 
"""

destroy_terraform_stack = """
Destroys resources related to a Terraform template or stack

Example:
        m3 destroy-terraform-stack --cloud <cloud_name> --template <name> --tenant <tenant_name> --template <name>
"""

plan_terraform_template = """
Plans the selected Terraform template

Examples:

1. Plans a Terraform template:
        m3 plan-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name>

2. Plans a Terraform template with a specific value for a string:
        m3 plan-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name> --variable <key:value>

3. Plans a Terraform template with a specific value for a list:
        m3 plan-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name> --variable <key:"value1,valueN">

4. Plans a Terraform template with a specific value for an object:
        m3 plan-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name> --variable <key1:"key2=value2">
        
5. Plans a Terraform template with multiple values, which can be a combination of strings, lists, and objects:
        m3 plan-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name> --variables "key1:\\\"value1_1,value1_2\\\",key2:value2,key3:\\\"key3_1=value3_1\\\""

6. Plans a Terraform template with specific values in a JSON file. Supported types: STRING, LIST, MAP, NUMBER, BOOL:
        m3 plan-terraform-template --cloud <cloud_name> --template <name> --tenant <tenant_name> --variables-file <path_to_file>
"""

total_report = """
Gets a total billing report for a tenant

Examples:
    1. For the current month (specify year and month):
        m3 total-report --tenant-group <tenant_group_name> --year <yyyy> --month <mm>

    2. For a specific day (specify year, month, and day):
        m3 total-report --tenant-group <tenant_group_name> --year <yyyy> --month <mm> --day <dd>

    3. For a date range (from - to):
        m3 total-report --tenant-group <tenant_group_name> --from <dd.mm.yyyy> --to <dd.mm.yyyy>

    4. Show only adjustments:
        m3 total-report --tenant-group <tenant_group_name> --year <yyyy> --month <mm> --day <dd> --adjustment

Note: Use either 'year' and 'month' (and optionally 'day'), OR 'from' and 'to'
"""

manage_key = """
Manage your SSH keys. Adds or deletes an SSH key in a region

Example:
        m3 manage-key--cloud <cloud_name> --key-name <name> --region <region_name> --action <action> --tenant <tenant_name>
"""

upload_script = """
Uploads an init script to tenant's library in Maestro

Example:
        m3 upload-script --cloud <cloud_name> --source-path <path> --script <script_name> --tenant <tenant_name>
"""

aws_management_console = """
Provides access to AWS management console for the specified tenant. The credentials are shared via an email access

Example:
        m3 aws-management-console --tenant <tenant_name> --access-type <access_type> 
"""

azure_management_console = """
Provides access to Azure management console for the specified tenant. (Access type DEFAULT)
The credentials are shared via an email

Example:
        m3 azure-management-console --tenant-name <tenant_name>
"""

google_management_console = """
Provides access to Google Cloud management console for the specified tenant. The credentials are shared via an email

Example:
        m3 google-management-console --tenant-name <tenant_name>
"""

cost_usage_report = """
Gets cost and usage optimization report

Example:
        m3 cost-usage-report --cloud <cloud> --date <dd.mm.yyyy> --region <region_name> --resource-type <resource_type> --tenant <tenant_name>
"""

untagged_resource_report = """
Provides the report by untagged resources within the specified tenant

Examples:

1.	Provides the general report for the tenant:
	    m3 untagged-resource-report --tenant <tenant_name> --from <dd.mm.yyyy> --to <dd.mm.yyyy>

2.	Provides the report for specific clouds:
        m3 untagged-resource-report --tenant <tenant_name> --from <dd.mm.yyyy> --to <dd.mm.yyyy> --cloud-list <cloud1>,<cloudN>
"""

create_attach_storage = """
Creates the storage and attaches to an existing instance

Example:
        m3 create-attach-storage --name <storage_name> --instance-id <instance_id> --tenant <tenant_name> --region <region_name> --size <size_GB> 
"""

detach_storage = """
Detaches the specified storage from an existing instance

Example:
        m3 detach-storage --tenant <tenant_name> --region <region_name> --instance-id <instance_id> --storage-id <storage_id>
"""

delete_storage = """
Removes the specified storage

Example:
        m3 delete-storage --tenant <tenant_name> --region <region_name> --storage-id <storage_id>
"""

cost_object_report = """
Gets cost object report for the specified tenant:

Example:
        m3 cost-object-report --tenant <tenant_name> --from <dd.mm.yyyy> --to <dd.mm.yyyy>
"""

allocate_ip = """
Allocate static ip in the specified region in tenant:

Example:
        m3 allocate-ip --tenant <tenant_name> --region <region_name>  --network <network_id>
"""

release_ip = """
Release static ip in the specified region in tenant:

Example:
        m3 release-ip --tenant <tenant_name> --region <region_name>  --ip <target_ip>
"""

describe_ip = """
Describe static ips in the specified region in tenant:

Example:
        m3 describe-ip --tenant <tenant_name> --region <region_name>
"""

describe_vlans = """
Describe available VLANs in the specified region in tenant:

Example:
        m3 describe-vlans --tenant <tenant_name> --region <region_name>
"""

deactivate_vlan = """
Deactivate specified VLAN in the specified region in tenant:

Example:
        m3 deactivate-vlan --tenant <tenant_name> --region <region_name> --vlan-name <vlan_name>
"""

activate_vlan = """
Activate specified VLAN in the specified region in tenant:

Example:
        m3 activate-vlan --tenant <tenant_name> --region <region_name> --vlan-name <vlan_name> --description <vlan_description>
"""

move_to_vlan = """
Move specific instance to another VLAN:

Example:
        m3 move-to-vlan --tenant <tenant_name> --region <region_name> --vlan-name <vlan_name> --instance-id <instance_id>
"""

associate_ip = """
Associate specific static IP with instance:

Example:
        m3 associate-ip --tenant <tenant_name> --region <region_name> --static-ip <ip> --instance-id <instance_id>
"""

disassociate_ip = """
Disassociate specific static IP from the instance:

Example:
        m3 disassociate-ip --tenant <tenant_name> --region <region_name> --static-ip <ip>
"""

multitenant_report = """
Gets multitenant billing report
    
Example:
    m3 multitenant-report --from <dd.mm.yyyy> --to <dd.mm.yyyy> --region <region_zone> --report-type <report_type> --include-billing-source
"""

billing_region_types = """
Gets billing region types

Example:
    m3 billing-region-types --all
"""

upload_terraform_template_from_git = """
Uploads a Terraform template from Git

Example:
    m3 upload-terraform-template-from-git --branch <branch_name> --cloud <cloud> --git-url <project_url> --storage <storage-type> --tenant <tenant>
                                        --template <name> --terraform-version <version> --token <personal_access_token> --webhook <action> 
                                        --variables "key1:\\\"value1_1,value1_2\\\",key2:value2,key3:\\\"key3_1=value3_1\\\"" OR --variables-file <path_to_file>
"""

describe_user_permissions = """
Describes the permission groups assigned to you in the specified tenant

Example:
    m3 describe-user-permissions --cloud <cloud> --tenant <tenant_name> --environment <environment>
"""

delete_service_section = """
Deletes the section content of the certain published service

Example:
1.	Deletes the section content and title:
	    m3 delete-service-section --section <section_name> --service <service_name> --block-title <title>

2.	Deletes blocks without a title in the section:
        m3 delete-service-section --section <section_name> --service <service_name> --delete-empty

3.	Deletes all the content of the section:
        m3 delete-service-section --section <section_name> --service <service_name> --delete-all
"""

describe_resources = """
Describes resources existing in a specific region for a specific tenant

Example:
    m3 describe-resources --region <region_name> --tenant <tenant_name>
"""

describe_insights = """
Describes insights for an instance in specific region for a specific tenant

Example:
    m3 describe-insights --instance-id <instance_id> --cloud <cloud_name> --region <region_name> --tenant <tenant_name> --availability_zone <required_for_google> --resource_group <required_for_azure>
"""

describe_service_section = """
Describes the section content of the certain published service

Example:
    m3 describe-service-section --service <service_name> --section <section_name> --block-title <title>
"""

manage_termination_protection = """
Manages termination protection for public cloud instances

Example:
    m3 manage-termination-protection --tenant <tenant_name> --region <region_name> --instance-id <instance_id> --action <action>
"""

decrypt_password = """
Decrypts the password for windows instances

Example:
    m3 decrypt-password --tenant <tenant_name> --region <region_name> --instance-id <instance_id> --private-key-path <private-key-path-to-file> --availability-zone <zone_name>
"""

backup = """
Provides assistance with using the Backup Platform Service for data backup and recovery

Example:
    m3 backup --tenant <tenant_name> --region <region_name> --cloud <cloud> --service-id <service-id> --instance-id <instance-id> --backup-server-id <backup-server-id>
"""

report = """
This command serves as a single point of entry for report-related commands:'total-report', 'subtotal-report', 'resource-report', and 'hourly-report'

Examples:

  Total, Subtotal, and Resource Reports:
    1. For the current month (specify year and month):
       m3 report --type total|subtotal|resource --tenant-group <tenant_group_name> --year <yyyy> --month <mm>

    2. For a specific day (specify year, month, and day):
       m3 report --type total|subtotal|resource --tenant-group <tenant_group_name> --year <yyyy> --month <mm> --day <dd>

  Hourly Report:
    m3 report --type hourly --tenant-group <tenant_group_name> --year <yyyy> --month <mm> --day <dd>
"""