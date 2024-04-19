import { Construct } from "constructs";
import {
  App,
  S3Backend,
  TerraformStack,
  // TerraformOutput,
} from "cdktf";
import { DockerProvider } from "@cdktf/provider-docker/lib/provider";
import { Image } from "@cdktf/provider-docker/lib/image";
import { Container } from "@cdktf/provider-docker/lib/container";
import { Network } from "@cdktf/provider-docker/lib/network";
import { AwsProvider } from "@cdktf/provider-aws/lib/provider";
// import { IamUser } from "@cdktf/provider-aws/lib/iam-user";
// import { DataAwsIamPolicyDocument } from "@cdktf/provider-aws/lib/data-aws-iam-policy-document";
import { IamPolicy } from "@cdktf/provider-aws/lib/iam-policy";
import { IamOpenidConnectProvider } from "@cdktf/provider-aws/lib/iam-openid-connect-provider";
import { IamRole } from "@cdktf/provider-aws/lib/iam-role";
import { IamRolePolicyAttachment } from "@cdktf/provider-aws/lib/iam-role-policy-attachment";
import { S3Bucket } from "@cdktf/provider-aws/lib/s3-bucket";
import { DataAwsIamUser } from "@cdktf/provider-aws/lib/data-aws-iam-user";
import { EcrRepository } from "@cdktf/provider-aws/lib/ecr-repository";
// import { DataAwsS3Bucket } from "@cdktf/provider-aws/lib/data-aws-s3-bucket";

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

class AwsStack extends TerraformStack {
  constructor(scope: Construct, name: string) {
    super(scope, name);

    new AwsProvider(this, "aws", {
      region: "us-east-1",
    });

    new S3Backend(this, {
      bucket: "terraform-state-bucket-f7354bbb",
      key: "terraform.tfstate",
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

const app = new App();
new DockerStack(app, "docker");
new AwsTerraformSetup(app, "aws-terraform-setup");
new AwsStack(app, "aws");
app.synth();
