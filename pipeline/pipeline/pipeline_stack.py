from aws_cdk import (
    aws_codepipeline,
    aws_codepipeline_actions,
    aws_ssm,
    aws_ecr,
    aws_codebuild,
    core
)


class PipelineStack(core.Stack):

    def _get_build_project(self):
        ecr = aws_ecr.Repository(
            self, "ECR",
            repository_name="arronmoore-dev",
            removal_policy=core.RemovalPolicy.DESTROY
        )

        cb_docker_build = aws_codebuild.PipelineProject(
            self, "DockerBuild",
            project_name=f"arronmoore-dev-docker-build",
            build_spec=aws_codebuild.BuildSpec.from_source_filename(
                filename='buildspec.yml'),
            environment=aws_codebuild.BuildEnvironment(
                privileged=True,
            ),
            # pass the ecr repo uri into the codebuild project so codebuild knows where to push
            environment_variables={
                'REPO_URI': aws_codebuild.BuildEnvironmentVariable(
                    value=ecr.repository_uri)
            },
            description='Pipeline for CodeBuild',
            timeout=core.Duration.minutes(60),
        )
        ecr.grant_pull_push(cb_docker_build)
        return ecr, cb_docker_build

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        try:
            with open('../.secrets/github_token.txt') as f:
                github_token = f.read()
        except FileNotFoundError:
            print("Create ../.secrets/github_token.txt and put the token which you create in the github interface into it.")

        source_output = aws_codepipeline.Artifact(artifact_name='source')

        ecr, cb_docker_build = self._get_build_project()

        pipeline = aws_codepipeline.Pipeline(
            self,
            "Pipeline",
            pipeline_name="cdk-pipeline",
            stages=[
                aws_codepipeline.StageProps(
                    stage_name='Source',
                    actions=[
                        aws_codepipeline_actions.GitHubSourceAction(
                            output=source_output,
                            action_name="Source",
                            oauth_token=core.SecretValue(github_token),
                            owner='arron1993',
                            repo="arronmoore.com",
                            branch="develop"
                        )
                    ]
                ),
                aws_codepipeline.StageProps(
                    stage_name='Build',
                    actions=[aws_codepipeline_actions.CodeBuildAction(
                        action_name='DockerBuildImages',
                        input=source_output,
                        project=cb_docker_build,
                        run_order=1,
                    )]
                )
            ]
        )
