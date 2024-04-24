import { Construct } from "constructs";
import { App, S3Backend, TerraformStack } from "cdktf";
import { DockerProvider } from "@cdktf/provider-docker/lib/provider";
import { Image } from "@cdktf/provider-docker/lib/image";
import { Container } from "@cdktf/provider-docker/lib/container";
import { Network } from "@cdktf/provider-docker/lib/network";
import { AwsProvider } from "@cdktf/provider-aws/lib/provider";
import { IamPolicy } from "@cdktf/provider-aws/lib/iam-policy";
import { IamOpenidConnectProvider } from "@cdktf/provider-aws/lib/iam-openid-connect-provider";
import { IamRole } from "@cdktf/provider-aws/lib/iam-role";
import { IamRolePolicyAttachment } from "@cdktf/provider-aws/lib/iam-role-policy-attachment";
import { S3Bucket } from "@cdktf/provider-aws/lib/s3-bucket";
import { DataAwsIamUser } from "@cdktf/provider-aws/lib/data-aws-iam-user";
import { EcrRepository } from "@cdktf/provider-aws/lib/ecr-repository";
import { Vpc } from "@cdktf/provider-aws/lib/vpc";
import { InternetGateway } from "@cdktf/provider-aws/lib/internet-gateway";
import { Subnet } from "@cdktf/provider-aws/lib/subnet";
import { RouteTable } from "@cdktf/provider-aws/lib/route-table";
import { RouteTableAssociation } from "@cdktf/provider-aws/lib/route-table-association";
import { SecurityGroup } from "@cdktf/provider-aws/lib/security-group";
import { EcsCluster } from "@cdktf/provider-aws/lib/ecs-cluster";
import { LaunchConfiguration } from "@cdktf/provider-aws/lib/launch-configuration";
import { AutoscalingGroup } from "@cdktf/provider-aws/lib/autoscaling-group";
import { EcsTaskDefinition } from "@cdktf/provider-aws/lib/ecs-task-definition";
import { EcsService } from "@cdktf/provider-aws/lib/ecs-service";
import { DataAwsEcrImage } from "@cdktf/provider-aws/lib/data-aws-ecr-image";
import { IamPolicyAttachment } from "@cdktf/provider-aws/lib/iam-policy-attachment";
import { IamInstanceProfile } from "@cdktf/provider-aws/lib/iam-instance-profile";
import { ServiceDiscoveryPrivateDnsNamespace } from "@cdktf/provider-aws/lib/service-discovery-private-dns-namespace";
import { ServiceDiscoveryService } from "@cdktf/provider-aws/lib/service-discovery-service";

const githubUsername = "Azeajr";
const githubRepo = "capturing_opportunities_capstone";

class DockerStack extends TerraformStack {
  constructor(scope: Construct, name: string) {
    super(scope, name);

    new DockerProvider(this, "docker", {});

    const appNetwork = new Network(this, "appNetwork", {
      name: "app_network",
    });
    const frontendImage = new Image(this, "frontendImage", {
      name: "react_frontend",
      keepLocally: true,
    });

    new Container(this, "frontendContainer", {
      name: "frontend",
      image: frontendImage.name,
      ports: [
        {
          internal: 3000,
          external: 3000,
        },
      ],
      networksAdvanced: [
        {
          name: appNetwork.name,
        },
      ],
      env: ["BACKEND_URL=http://backend:8000", "BACKEND_API_KEY=devsecret"],
    });

    const backendImage = new Image(this, "backendImage", {
      name: "fastapi_backend",
      keepLocally: true,
    });

    new Container(this, "backendContainer", {
      name: "backend",
      image: backendImage.name,
      networksAdvanced: [
        {
          name: appNetwork.name,
        },
      ],
      env: ["env=dev", "API_KEY=devsecret"],
    });
  }
}

class AwsTerraformSetup extends TerraformStack {
  constructor(scope: Construct, name: string) {
    super(scope, name);

    new AwsProvider(this, "aws", {
      region: "us-east-1",
    });

    const iamUser = new DataAwsIamUser(this, "iamUser", {
      userName: "viablespark343",
    });

    // S3 Backend for Terraform
    const bucket = new S3Bucket(this, "TerraformStateBucket", {
      bucket: "terraform-state-bucket-f7354bbb",
    });

    const iamPolicy = new IamPolicy(this, "TerraformStateAccessPolicy", {
      name: "terraform-state-access-policy",
      policy: JSON.stringify({
        Version: "2012-10-17",
        Statement: [
          {
            Effect: "Allow",
            Action: "s3:ListBucket",
            Resource: bucket.arn,
          },
          {
            Effect: "Allow",
            Action: ["s3:GetObject", "s3:PutObject"],
            Resource: `${bucket.arn}/*`,
          },
        ],
      }),
    });
    const iamRole = new IamRole(this, "TerraformStateAccessRole", {
      name: "terraform-state-access-role",
      assumeRolePolicy: JSON.stringify({
        Version: "2012-10-17",
        Statement: [
          {
            Effect: "Allow",
            Principal: {
              AWS: iamUser.arn,
            },
            Action: "sts:AssumeRole",
          },
        ],
      }),
    });

    new IamRolePolicyAttachment(
      this,
      "TerraformStateAccessRolePolicyAttachment",
      {
        role: iamRole.name,
        policyArn: iamPolicy.arn,
      }
    );
  }
}

class GithubEcrActionStack extends TerraformStack {
  constructor(scope: Construct, name: string) {
    super(scope, name);

    new AwsProvider(this, "aws", {
      region: "us-east-1",
    });

    new S3Backend(this, {
      bucket: "terraform-state-bucket-f7354bbb",
      key: "github-ecr-action-stack.tfstate",
      region: "us-east-1",
    });

    const backendRepository = new EcrRepository(this, "backendRepository", {
      name: "backend",
    });

    const frontendRepository = new EcrRepository(this, "frontendRepository", {
      name: "frontend",
    });

    // echo | openssl s_client -showcerts -servername token.actions.githubusercontent.com -connect token.actions.githubusercontent.com:443 2>/dev/null | openssl x509 -fingerprint -noout -sha1 | cut -f2 -d'=' | tr -d ':' | tr '[:upper:]' '[:lower:]'
    const oidcProvider = new IamOpenidConnectProvider(this, "oidcProvider", {
      clientIdList: ["sts.amazonaws.com"],
      thumbprintList: ["959cb2b52b4ad201a593847abca32ff48f838c2e"],
      url: "https://token.actions.githubusercontent.com",
    });

    const githubActionsRole = new IamRole(this, "githubActionsRole", {
      name: "github-actions-role",
      assumeRolePolicy: JSON.stringify({
        Version: "2012-10-17",
        Statement: [
          {
            Effect: "Allow",
            Principal: {
              Federated: oidcProvider.arn,
            },
            Action: "sts:AssumeRoleWithWebIdentity",
            Condition: {
              StringLike: {
                "token.actions.githubusercontent.com:sub": `repo:${githubUsername}/${githubRepo}*`,
              },
              StringEquals: {
                "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
              },
            },
          },
        ],
      }),
    });

    const githubActionsPolicy = new IamPolicy(this, "githubActionsPolicy", {
      policy: JSON.stringify({
        Version: "2012-10-17",
        Statement: [
          {
            Effect: "Allow",
            Action: ["ecr:GetAuthorizationToken"],
            Resource: "*",
          },
          {
            Effect: "Allow",
            Action: [
              "ecr:GetAuthorizationToken",
              "ecr:BatchCheckLayerAvailability",
              "ecr:GetDownloadUrlForLayer",
              "ecr:GetRepositoryPolicy",
              "ecr:DescribeRepositories",
              "ecr:ListImages",
              "ecr:DescribeImages",
              "ecr:BatchGetImage",
              "ecr:GetLifecyclePolicy",
              "ecr:GetLifecyclePolicyPreview",
              "ecr:ListTagsForResource",
              "ecr:DescribeImageScanFindings",
              "ecr:InitiateLayerUpload",
              "ecr:UploadLayerPart",
              "ecr:CompleteLayerUpload",
              "ecr:PutImage",
            ],
            Resource: backendRepository.arn,
          },
          {
            Effect: "Allow",
            Action: [
              "ecr:GetAuthorizationToken",
              "ecr:BatchCheckLayerAvailability",
              "ecr:GetDownloadUrlForLayer",
              "ecr:GetRepositoryPolicy",
              "ecr:DescribeRepositories",
              "ecr:ListImages",
              "ecr:DescribeImages",
              "ecr:BatchGetImage",
              "ecr:GetLifecyclePolicy",
              "ecr:GetLifecyclePolicyPreview",
              "ecr:ListTagsForResource",
              "ecr:DescribeImageScanFindings",
              "ecr:InitiateLayerUpload",
              "ecr:UploadLayerPart",
              "ecr:CompleteLayerUpload",
              "ecr:PutImage",
            ],
            Resource: frontendRepository.arn,
          },
        ],
      }),
    });

    new IamRolePolicyAttachment(this, "githubActionsRolePolicyAttachment", {
      role: githubActionsRole.name,
      policyArn: githubActionsPolicy.arn,
    });
  }
}

class DeployApplicationStack extends TerraformStack {
  constructor(scope: Construct, name: string) {
    super(scope, name);

    new AwsProvider(this, "aws", {
      region: "us-east-1",
    });

    new S3Backend(this, {
      bucket: "terraform-state-bucket-f7354bbb",
      key: "deploy-application-stack.tfstate",
      region: "us-east-1",
    });

    // Create an IAM Role for ECS Instances
    const ecsInstanceRole = new IamRole(this, "ecsInstanceRole", {
      name: "ecsInstanceRole",
      assumeRolePolicy: JSON.stringify({
        Version: "2012-10-17",
        Statement: [
          {
            Effect: "Allow",
            Principal: { Service: "ec2.amazonaws.com" },
            Action: "sts:AssumeRole",
          },
        ],
      }),
    });

    // Attach the Amazon ECS managed policies
    new IamPolicyAttachment(this, "ecsInstancePolicy", {
      name: "ecsInstancePolicy",
      roles: [ecsInstanceRole.name],
      policyArn:
        "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role",
    });

    // Attach the Amazon ECR Read-Only policy
    new IamPolicyAttachment(this, "ecrReadOnlyPolicy", {
      name: "ecrReadOnlyPolicy",
      roles: [ecsInstanceRole.name],
      policyArn: "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
    });

    // Create an IAM Instance Profile for the ECS Instances
    const ecsInstanceProfile = new IamInstanceProfile(
      this,
      "ecsInstanceProfile",
      {
        name: "ecsInstanceProfile",
        role: ecsInstanceRole.name,
      }
    );

    const backendImage = new DataAwsEcrImage(this, "backendImage", {
      repositoryName: "backend",
      imageTag: "latest",
    });

    const frontendImage = new DataAwsEcrImage(this, "frontendImage", {
      repositoryName: "frontend",
      imageTag: "latest",
    });

    const appVpc = new Vpc(this, "AppVpc", {
      cidrBlock: "10.0.0.0/16",
      enableDnsSupport: true,
      enableDnsHostnames: true,
      tags: { Name: "MyAppVPC" },
    });

    const dnsNamespace = new ServiceDiscoveryPrivateDnsNamespace(this, "DnsNamespace", {
      name: "myapp.local",
      vpc: appVpc.id,
    });

    const backendServiceDiscovery = new ServiceDiscoveryService(this, "BackendServiceDiscovery", {
      name: "backend",
      namespaceId: dnsNamespace.id,
      dnsConfig: {
        namespaceId: dnsNamespace.id,
        dnsRecords: [{ type: "A", ttl: 10 }],
      },
      healthCheckCustomConfig: { failureThreshold: 1 },
    });

    const igw = new InternetGateway(this, "AppIgw", {
      vpcId: appVpc.id,
      tags: { Name: "MyAppIGW" },
    });

    const publicSubnet = new Subnet(this, "AppPublicSubnet", {
      vpcId: appVpc.id,
      cidrBlock: "10.0.1.0/24",
      availabilityZone: "us-east-1a",
      mapPublicIpOnLaunch: true,
      tags: { Name: "MyAppPublicSubnet" },
    });

    const privateSubnet = new Subnet(this, "AppPrivateSubnet", {
      vpcId: appVpc.id,
      cidrBlock: "10.0.2.0/24",
      availabilityZone: "us-east-1b",
      mapPublicIpOnLaunch: false,
      tags: { Name: "MyAppPrivateSubnet" },
    });

    const publicRouteTable = new RouteTable(this, "PublicRouteTable", {
      vpcId: appVpc.id,
      route: [{ cidrBlock: "0.0.0.0/0", gatewayId: igw.id }],
      tags: { Name: "PublicRouteTable" },
    });

    new RouteTableAssociation(this, "PublicRouteTableAssoc", {
      subnetId: publicSubnet.id,
      routeTableId: publicRouteTable.id,
    });

    const privateRouteTable = new RouteTable(this, "PrivateRouteTable", {
      vpcId: appVpc.id,
      tags: { Name: "PrivateRouteTable" },
    });

    new RouteTableAssociation(this, "PrivateRouteTableAssoc", {
      subnetId: privateSubnet.id,
      routeTableId: privateRouteTable.id,
    });

    // Security Groups for Frontend and Backend
    const frontendSecurityGroup = new SecurityGroup(
      this,
      "FrontendSecurityGroup",
      {
        vpcId: appVpc.id,
        description: "Security group for the frontend",
        ingress: [
          {
            fromPort: 80,
            toPort: 80,
            protocol: "tcp",
            cidrBlocks: ["0.0.0.0/0"],
          },
          {
            fromPort: 443,
            toPort: 443,
            protocol: "tcp",
            cidrBlocks: ["0.0.0.0/0"],
          },
        ],
        egress: [
          {
            fromPort: 0,
            toPort: 0,
            protocol: "-1",
            cidrBlocks: ["0.0.0.0/0"],
          },
        ],
        tags: { Name: "FrontendSG" },
      }
    );

    const backendSecurityGroup = new SecurityGroup(
      this,
      "BackendSecurityGroup",
      {
        vpcId: appVpc.id,
        description: "Security group for the backend",
        ingress: [
          {
            fromPort: 8000,
            toPort: 8000,
            protocol: "tcp",
            securityGroups: [frontendSecurityGroup.id], // Only allow traffic from the frontend security group
          },
        ],
        egress: [
          {
            fromPort: 0,
            toPort: 0,
            protocol: "-1",
            cidrBlocks: ["0.0.0.0/0"],
          },
        ],
        tags: { Name: "BackendSG" },
      }
    );

    // ECS Cluster
    const ecsCluster = new EcsCluster(this, "EcsCluster", {
      name: "MyAppCluster",
      tags: { Name: "MyAppCluster" },
    });

    // Launch Configuration for Frontend
    const frontendLaunchConfig = new LaunchConfiguration(
      this,
      "FrontendLaunchConfig",
      {
        imageId: "ami-04e5276ebb8451442",
        instanceType: "t2.micro",
        securityGroups: [frontendSecurityGroup.id],
        iamInstanceProfile: ecsInstanceProfile.name,
        userData: `#!/bin/bash
echo ECS_CLUSTER=${ecsCluster.name} > /etc/ecs/ecs.config`,
      }
    );

    // Launch Configuration for Backend
    const backendLaunchConfig = new LaunchConfiguration(
      this,
      "BackendLaunchConfig",
      {
        imageId: "ami-04e5276ebb8451442",
        instanceType: "t2.micro",
        // instanceType: "g4dn.xlarge",
        securityGroups: [backendSecurityGroup.id],
        iamInstanceProfile: ecsInstanceProfile.name,
        userData: `#!/bin/bash
echo ECS_CLUSTER=${ecsCluster.name} > /etc/ecs/ecs.config`,
      }
    );

    new AutoscalingGroup(this, "FrontendASG", {
      launchConfiguration: frontendLaunchConfig.id,
      minSize: 1,
      maxSize: 2,
      desiredCapacity: 1,
      vpcZoneIdentifier: [publicSubnet.id],
    });

    new AutoscalingGroup(this, "BackendASG", {
      launchConfiguration: backendLaunchConfig.id,
      minSize: 1,
      maxSize: 1,
      desiredCapacity: 1,
      vpcZoneIdentifier: [privateSubnet.id],
    });

    // ECS Task Definitions for Frontend
    const frontendTaskDefinition = new EcsTaskDefinition(
      this,
      "FrontendTaskDefinition",
      {
        family: "my-app-frontend",
        networkMode: "awsvpc",
        requiresCompatibilities: ["EC2"],
        cpu: "256",
        memory: "512",
        containerDefinitions: JSON.stringify([
          {
            name: "frontend",
            image: frontendImage.imageUri,
            essential: true,
            cpu: 128,
            memory: 256,
            portMappings: [
              {
                containerPort: 3000,
                hostPort: 3000,
              },
            ],
            environment: [
              {
                name: "BACKEND_URL",
                value: "http://backend.services.local:8000",
              },
              {
                name: "BACKEND_API_KEY",
                value: "devsecret",
              },
            ],
          },
        ]),
      }
    );

    // ECS Task Definitions for Backend
    const backendTaskDefinition = new EcsTaskDefinition(
      this,
      "BackendTaskDefinition",
      {
        family: "my-app-backend",
        networkMode: "awsvpc",
        requiresCompatibilities: ["EC2"],
        cpu: "256",
        memory: "512",
        containerDefinitions: JSON.stringify([
          {
            name: "backend",
            image: backendImage.imageUri,
            essential: true,
            cpu: 128,
            memory: 256,
            portMappings: [
              {
                containerPort: 8000,
                hostPort: 8000,
              },
            ],
          },
        ]),
      }
    );

    // ECS Services for Frontend
    new EcsService(this, "FrontendService", {
      name: "MyAppFrontendService",
      cluster: ecsCluster.id,
      taskDefinition: frontendTaskDefinition.arn,
      desiredCount: 1,
      launchType: "EC2",
      networkConfiguration: {
        subnets: [publicSubnet.id],
        securityGroups: [frontendSecurityGroup.id],
      },
    });

    // ECS Services for Backend
    new EcsService(this, "BackendService", {
      name: "MyAppBackendService",
      cluster: ecsCluster.id,
      taskDefinition: backendTaskDefinition.arn,
      desiredCount: 1,
      launchType: "EC2",
      networkConfiguration: {
        subnets: [privateSubnet.id],
        securityGroups: [backendSecurityGroup.id],
        assignPublicIp: false, // Backend does not need to be directly accessible from the Internet
      },
      serviceRegistries: {
        registryArn: backendServiceDiscovery.arn,
        containerName: "backend",
      }
    });
  }
}

const app = new App();
new DockerStack(app, "docker");
new AwsTerraformSetup(app, "aws-terraform-setup");
new GithubEcrActionStack(app, "github-ecr-action-stack");
new DeployApplicationStack(app, "deploy-application-stack");
app.synth();
