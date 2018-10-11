#!/bin/bash

image_family="pytorch-latest-cu92"
zone="us-west1-a"
instance_name="delete-me-pytorch-gpu"
gpu_type="nvidia-tesla-p100"
gpu_count="1"

while getopts ":i:z:n:g:c" opt; do
  case $opt in
    i) image_family="$OPTARG"
    ;;
    z) zone="$OPTARG"
    ;;
    n) instance_name="$OPTARG"
	;;
	g) gpu_type="$OPTARG"
	;;
	c) gpu_count="$OPTARG"
	;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

# gcloud compute instances create $instance_name \
#	--zone=$zone \
#	--image-family=$image_family \
#	--maintenance-policy=TERMINATE \
#	--accelerator="type=${gpu_type},count=${gpu_count}" \
#	--metadata='install-nvidia-driver=True' \
#	--service-account='data-science-2@manymoons-215635.iam.gserviceaccount.com'

# TODO: Investigate if we should use scopes (https://cloud.google.com/compute/docs/access/create-enable-service-accounts-for-instances)


printf "Argument image_family is %s\n" "$image_family"
printf "Argument zone is %s\n" "$zone"
printf "Argument instance_name is %s\n" "$instance_name"
printf "Argument gpu_type is %s\n" "$gpu_type"
printf "Argument gpu_count is %s\n" "$gpu_count"
printf "type=${gpu_type},count=${gpu_count}"