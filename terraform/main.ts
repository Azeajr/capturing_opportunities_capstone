import { Construct } from "constructs";
// import { AwsProvider } from "@cdktf/provider-aws/lib/provider";
import {
  App,
  TerraformStack,
  // S3Backend,
  // S3BackendConfig,
} from "cdktf";
import { DockerProvider } from "@cdktf/provider-docker/lib/provider";
import { Image } from "@cdktf/provider-docker/lib/image";
import { Container } from "@cdktf/provider-docker/lib/container";
import * as dotenv from "dotenv";

class MyStack extends TerraformStack {
  constructor(scope: Construct, name: string) {
    super(scope, name);

    const { AWS_REGION, AWS_BUCKET, AWS_BUCKET_PATH } = dotenv.config().parsed!;
    console.log(AWS_REGION, AWS_BUCKET, AWS_BUCKET_PATH);

    // const region = "us-west-2";
    // const bucket = "nguyen-zea";
    // const bucketPath = "capturing-opertuinites/terraform-state";

    // new AwsProvider(this, "aws", {
    //   region,
    // });

    // const s3StateProperties: S3BackendConfig = {
    //   region,
    //   key: `${bucketPath}/terraform.tfstate`,
    //   bucket,
    // };

    // new S3Backend(this, s3StateProperties);

    new DockerProvider(this, "docker", {});

    const dockerImage = new Image(this, "nginxImage", {
      name: "nginx:latest",
      keepLocally: false,
    });

    new Container(this, "nginxContainer", {
      name: "frontend",
      image: dockerImage.name,
      ports: [
        {
          internal: 80,
          external: 8000,
        },
      ],
    });

    // const pythonImage = new Image(this, "pythonImage", {
    //   name: "python:3.9",
    //   keepLocally: false,
    // });

    // const fastapiImage = new Image(this, "fastapiImage", {
    //   name: "fastapi_backend",
    //   keepLocally: false,
    // });

    new Container(this, "backendContainer", {
      name: "backend",
      image: "fastapi_backend",
      ports: [
        {
          internal: 5000,
          external: 5000,
        },
      ],
    });
  }
}

const app = new App();
new MyStack(app, "terraform");
app.synth();
