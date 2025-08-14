#!/usr/bin/env python3
"""
AWS Public Endpoints MCP Server - 간단 버전
AWS 서비스의 외부 엔드포인트를 스캔하는 MCP 서버
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aws-public-endpoints")

# MCP 서버 초기화
server = Server("aws-public-endpoints")


class PublicEndpointsFinder:
    """AWS 외부 엔드포인트 검색 클래스"""

    def __init__(self, region: str = "us-east-1", profile: Optional[str] = None):
        self.region = region
        self.session = (
            boto3.Session(profile_name=profile) if profile else boto3.Session()
        )

    def get_client(self, service: str):
        """AWS 클라이언트 생성"""
        return self.session.client(service, region_name=self.region)

    async def find_ec2_endpoints(self) -> List[Dict[str, Any]]:
        """EC2 퍼블릭 인스턴스 검색"""
        endpoints = []
        try:
            ec2 = self.get_client("ec2")
            response = ec2.describe_instances()

            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    if instance.get("PublicIpAddress"):
                        endpoints.append(
                            {
                                "id": instance["InstanceId"],
                                "public_ip": instance["PublicIpAddress"],
                                "public_dns": instance.get("PublicDnsName", ""),
                                "state": instance["State"]["Name"],
                            }
                        )
        except ClientError as e:
            logger.error(f"EC2 스캔 오류: {e}")

        return endpoints

    async def find_elb_endpoints(self) -> List[Dict[str, Any]]:
        """로드밸런서 엔드포인트 검색"""
        endpoints = []
        try:
            # ALB/NLB
            elbv2 = self.get_client("elbv2")
            response = elbv2.describe_load_balancers()

            for lb in response["LoadBalancers"]:
                if lb["Scheme"] == "internet-facing":
                    endpoints.append(
                        {
                            "id": lb["LoadBalancerName"],
                            "dns_name": lb["DNSName"],
                            "type": lb["Type"],
                            "state": lb["State"]["Code"],
                        }
                    )
        except ClientError as e:
            logger.error(f"ELB 스캔 오류: {e}")

        return endpoints

    async def find_s3_endpoints(self) -> List[Dict[str, Any]]:
        """S3 버킷 목록 검색"""
        endpoints = []
        try:
            s3 = self.get_client("s3")
            response = s3.list_buckets()

            for bucket in response["Buckets"]:
                bucket_name = bucket["Name"]
                endpoints.append(
                    {
                        "id": bucket_name,
                        "url": f"https://{bucket_name}.s3.amazonaws.com",
                        "created": bucket["CreationDate"].isoformat(),
                    }
                )
        except ClientError as e:
            logger.error(f"S3 스캔 오류: {e}")

        return endpoints

    async def find_api_endpoints(self) -> List[Dict[str, Any]]:
        """API Gateway 엔드포인트 검색"""
        endpoints = []
        try:
            # REST API
            api = self.get_client("apigateway")
            response = api.get_rest_apis()

            for rest_api in response["items"]:
                endpoints.append(
                    {
                        "id": rest_api["id"],
                        "name": rest_api["name"],
                        "url": f"https://{rest_api['id']}.execute-api.{self.region}.amazonaws.com",
                        "type": "REST",
                    }
                )
        except ClientError as e:
            logger.error(f"API Gateway 스캔 오류: {e}")

        return endpoints

    async def scan_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """모든 서비스 스캔"""
        logger.info(f"리전 {self.region} 스캔 시작")

        # 병렬로 모든 서비스 스캔
        tasks = [
            self.find_ec2_endpoints(),
            self.find_elb_endpoints(),
            self.find_s3_endpoints(),
            self.find_api_endpoints(),
        ]
        
        ec2_results, elb_results, s3_results, api_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = {
            "EC2": ec2_results if isinstance(ec2_results, list) else [],
            "ELB": elb_results if isinstance(elb_results, list) else [],
            "S3": s3_results if isinstance(s3_results, list) else [],
            "API Gateway": api_results if isinstance(api_results, list) else [],
        }

        total = sum(len(endpoints) for endpoints in results.values())
        logger.info(f"총 {total}개 엔드포인트 발견")

        return results


@server.list_tools()
async def list_tools() -> List[Tool]:
    """사용 가능한 도구 목록"""
    return [
        Tool(
            name="scan_public_endpoints",
            description="AWS 퍼블릭 엔드포인트 스캔",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "AWS 리전 (기본값: us-east-1)",
                        "default": "us-east-1",
                    },
                    "profile": {
                        "type": "string",
                        "description": "AWS 프로파일 (선택사항)",
                    },
                },
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """도구 실행"""

    if name == "scan_public_endpoints":
        region = arguments.get("region", "us-east-1")
        profile = arguments.get("profile")

        try:
            finder = PublicEndpointsFinder(region=region, profile=profile)
            results = await finder.scan_all()

            # 결과 포맷팅
            output = f"# AWS 퍼블릭 엔드포인트 스캔 결과\n\n"
            output += f"**리전:** {region}\n"
            if profile:
                output += f"**프로파일:** {profile}\n"

            total = sum(len(endpoints) for endpoints in results.values())
            output += f"**총 발견 개수:** {total}\n\n"

            for service, endpoints in results.items():
                output += f"## {service} ({len(endpoints)}개)\n\n"

                if not endpoints:
                    output += "발견된 엔드포인트 없음\n\n"
                    continue

                for endpoint in endpoints:
                    output += f"- **{endpoint['id']}**\n"
                    for key, value in endpoint.items():
                        if key != "id" and value:
                            output += f"  - {key}: {value}\n"
                    output += "\n"

            return [TextContent(type="text", text=output)]

        except NoCredentialsError:
            return [
                TextContent(type="text", text="오류: AWS 자격증명을 찾을 수 없습니다.")
            ]
        except Exception as e:
            return [TextContent(type="text", text=f"오류: {str(e)}")]

    return [TextContent(type="text", text=f"알 수 없는 도구: {name}")]


async def main():
    """서버 실행"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="aws-public-endpoints",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
