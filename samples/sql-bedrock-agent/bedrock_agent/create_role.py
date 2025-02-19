from aws_cdk import (
    # Duration,
    Stack,
    aws_iam as iam,
)
from constructs import Construct


class CreateAgentRole(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)
        _account = stk.account
        _region = stk.region
        _stack_name = stk.stack_name

        self.kb_service_role = iam.Role(
            self,
            "Kb",
            role_name=f"AmazonBedrockExecutionRoleForAgents_{_stack_name}",
            assumed_by=iam.ServicePrincipal(
                "bedrock.amazonaws.com",
                conditions={
                    "StringEquals": {"aws:SourceAccount": _account},
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock:{_region}:{_account}:agent/*"
                    },
                },
            ),
        )
        # Added support for cross-region inference
        self.kb_service_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["bedrock:InvokeModel*"],
                resources=[
                    "arn:aws:bedrock:us-east-1::foundation-model/*",
                    "arn:aws:bedrock:us-east-2::foundation-model/*",
                    "arn:aws:bedrock:us-west-2::foundation-model/*",
                    f"arn:aws:bedrock:{_region}:{_account}:inference-profile/*",
                ],
            )
        )

        self.kb_service_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:GetInferenceProfile",
                    "bedrock:ListInferenceProfiles",
                ],
                resources=[
                    "arn:aws:bedrock:*:*:inference-profile/*",
                    "arn:aws:bedrock:*:*:application-inference-profile/*",
                ],
            )
        )

        self.knowledge_base_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["bedrock:Retrieve"],
            resources=[f"arn:aws:bedrock:{_region}:{_account}:knowledge-base/*"],
        )

        self.kb_service_role.add_to_policy(self.knowledge_base_policy)
        self.arn = self.kb_service_role.role_arn
