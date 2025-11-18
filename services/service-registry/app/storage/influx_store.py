"""
InfluxDB Storage Layer for Service Registry
Provides time-series storage for historical metrics and monitoring
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger(__name__)


class InfluxServiceStore:
    """
    InfluxDB-based storage for service metrics and historical data
    Optimized for time-series queries and analytics
    """

    def __init__(self, url: str, token: str, org: str, bucket: str):
        """
        Initialize InfluxDB storage

        Args:
            url: InfluxDB URL
            token: Authentication token
            org: Organization name
            bucket: Bucket name for storing metrics
        """
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.org = org
        self.bucket = bucket

        logger.info(f"✅ InfluxDB client initialized: {url}")

    def write_service_metric(
        self,
        service_name: str,
        status: str,
        response_time: float,
        address: str,
        port: int,
        additional_fields: Optional[Dict] = None,
    ) -> bool:
        """
        Write service health metric to InfluxDB

        Args:
            service_name: Name of the service
            status: Health status (healthy, down, etc.)
            response_time: Response time in milliseconds
            address: Service IP address
            port: Service port
            additional_fields: Additional metric fields

        Returns:
            bool: True if successful
        """
        try:
            # Create data point
            point = (
                Point("service_health")
                .tag("service_name", service_name)
                .tag("status", status)
                .tag("address", address)
                .tag("port", str(port))
                .field("response_time", response_time)
                .field("is_healthy", 1 if status == "healthy" else 0)
                .time(datetime.utcnow(), WritePrecision.NS)
            )

            # Add additional fields if provided
            if additional_fields:
                for key, value in additional_fields.items():
                    point = point.field(key, value)

            # Write to InfluxDB
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)

            return True

        except Exception as e:
            logger.error(f"❌ Error writing metric to InfluxDB: {e}")
            return False

    def write_registration_event(
        self, service_name: str, hostname: str, address: str, port: int
    ) -> bool:
        """
        Write service registration event

        Args:
            service_name: Name of the service
            hostname: Service hostname
            address: Service IP address
            port: Service port

        Returns:
            bool: True if successful
        """
        try:
            point = (
                Point("service_registration")
                .tag("service_name", service_name)
                .tag("hostname", hostname)
                .tag("address", address)
                .tag("port", str(port))
                .field("event_type", "registered")
                .field("count", 1)
                .time(datetime.utcnow(), WritePrecision.NS)
            )

            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            return True

        except Exception as e:
            logger.error(f"❌ Error writing registration event: {e}")
            return False

    def write_deregistration_event(self, service_name: str) -> bool:
        """
        Write service deregistration event

        Args:
            service_name: Name of the service

        Returns:
            bool: True if successful
        """
        try:
            point = (
                Point("service_registration")
                .tag("service_name", service_name)
                .field("event_type", "deregistered")
                .field("count", 1)
                .time(datetime.utcnow(), WritePrecision.NS)
            )

            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            return True

        except Exception as e:
            logger.error(f"❌ Error writing deregistration event: {e}")
            return False

    def get_service_uptime(
        self, service_name: str, hours: int = 24
    ) -> Optional[float]:
        """
        Calculate service uptime percentage

        Args:
            service_name: Name of the service
            hours: Number of hours to look back

        Returns:
            Uptime percentage (0-100) or None if error
        """
        try:
            query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -{hours}h)
                |> filter(fn: (r) => r._measurement == "service_health")
                |> filter(fn: (r) => r.service_name == "{service_name}")
                |> filter(fn: (r) => r._field == "is_healthy")
                |> mean()
            '''

            result = self.query_api.query(org=self.org, query=query)

            # Extract uptime percentage
            for table in result:
                for record in table.records:
                    uptime = record.get_value() * 100
                    return round(uptime, 2)

            return None

        except Exception as e:
            logger.error(f"❌ Error calculating uptime for {service_name}: {e}")
            return None

    def get_average_response_time(
        self, service_name: str, hours: int = 24
    ) -> Optional[float]:
        """
        Get average response time for a service

        Args:
            service_name: Name of the service
            hours: Number of hours to look back

        Returns:
            Average response time in milliseconds or None if error
        """
        try:
            query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -{hours}h)
                |> filter(fn: (r) => r._measurement == "service_health")
                |> filter(fn: (r) => r.service_name == "{service_name}")
                |> filter(fn: (r) => r._field == "response_time")
                |> mean()
            '''

            result = self.query_api.query(org=self.org, query=query)

            for table in result:
                for record in table.records:
                    avg_time = record.get_value()
                    return round(avg_time, 2)

            return None

        except Exception as e:
            logger.error(
                f"❌ Error calculating avg response time for {service_name}: {e}"
            )
            return None

    def get_service_history(
        self, service_name: str, hours: int = 24, interval: str = "5m"
    ) -> List[Dict]:
        """
        Get service health history with aggregation

        Args:
            service_name: Name of the service
            hours: Number of hours to look back
            interval: Aggregation interval (e.g., "5m", "1h")

        Returns:
            List of historical data points
        """
        try:
            query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -{hours}h)
                |> filter(fn: (r) => r._measurement == "service_health")
                |> filter(fn: (r) => r.service_name == "{service_name}")
                |> filter(fn: (r) => r._field == "response_time" or r._field == "is_healthy")
                |> aggregateWindow(every: {interval}, fn: mean, createEmpty: false)
            '''

            result = self.query_api.query(org=self.org, query=query)

            history = []
            for table in result:
                for record in table.records:
                    history.append(
                        {
                            "timestamp": record.get_time().isoformat(),
                            "field": record.get_field(),
                            "value": record.get_value(),
                        }
                    )

            return history

        except Exception as e:
            logger.error(f"❌ Error getting history for {service_name}: {e}")
            return []

    def get_all_services_uptime(self, hours: int = 24) -> List[Dict]:
        """
        Get uptime for all services

        Args:
            hours: Number of hours to look back

        Returns:
            List of service uptime data
        """
        try:
            query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -{hours}h)
                |> filter(fn: (r) => r._measurement == "service_health")
                |> filter(fn: (r) => r._field == "is_healthy")
                |> group(columns: ["service_name"])
                |> mean()
            '''

            result = self.query_api.query(org=self.org, query=query)

            uptime_data = []
            for table in result:
                for record in table.records:
                    service_name = record.values.get("service_name")
                    uptime = record.get_value() * 100

                    uptime_data.append(
                        {"service_name": service_name, "uptime_percent": round(uptime, 2)}
                    )

            return uptime_data

        except Exception as e:
            logger.error(f"❌ Error getting all services uptime: {e}")
            return []

    def get_downtime_events(
        self, service_name: str, hours: int = 24
    ) -> List[Dict]:
        """
        Get downtime events for a service

        Args:
            service_name: Name of the service
            hours: Number of hours to look back

        Returns:
            List of downtime events
        """
        try:
            query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -{hours}h)
                |> filter(fn: (r) => r._measurement == "service_health")
                |> filter(fn: (r) => r.service_name == "{service_name}")
                |> filter(fn: (r) => r.status == "down")
                |> filter(fn: (r) => r._field == "is_healthy")
            '''

            result = self.query_api.query(org=self.org, query=query)

            downtime_events = []
            for table in result:
                for record in table.records:
                    downtime_events.append(
                        {
                            "timestamp": record.get_time().isoformat(),
                            "status": record.values.get("status"),
                        }
                    )

            return downtime_events

        except Exception as e:
            logger.error(f"❌ Error getting downtime events for {service_name}: {e}")
            return []

    def get_response_time_percentiles(
        self, service_name: str, hours: int = 24
    ) -> Optional[Dict]:
        """
        Get response time percentiles (p50, p95, p99)

        Args:
            service_name: Name of the service
            hours: Number of hours to look back

        Returns:
            Dictionary with percentile data or None
        """
        try:
            percentiles = {}

            for p in [50, 95, 99]:
                query = f'''
                from(bucket: "{self.bucket}")
                    |> range(start: -{hours}h)
                    |> filter(fn: (r) => r._measurement == "service_health")
                    |> filter(fn: (r) => r.service_name == "{service_name}")
                    |> filter(fn: (r) => r._field == "response_time")
                    |> quantile(q: {p / 100.0})
                '''

                result = self.query_api.query(org=self.org, query=query)

                for table in result:
                    for record in table.records:
                        percentiles[f"p{p}"] = round(record.get_value(), 2)

            return percentiles if percentiles else None

        except Exception as e:
            logger.error(f"❌ Error getting percentiles for {service_name}: {e}")
            return None

    def get_service_metrics_summary(self, service_name: str, hours: int = 24) -> Dict:
        """
        Get comprehensive metrics summary for a service

        Args:
            service_name: Name of the service
            hours: Number of hours to look back

        Returns:
            Dictionary with comprehensive metrics
        """
        try:
            uptime = self.get_service_uptime(service_name, hours)
            avg_response_time = self.get_average_response_time(service_name, hours)
            percentiles = self.get_response_time_percentiles(service_name, hours)
            downtime_events = self.get_downtime_events(service_name, hours)

            return {
                "service_name": service_name,
                "period_hours": hours,
                "uptime_percent": uptime,
                "average_response_time": avg_response_time,
                "response_time_percentiles": percentiles,
                "downtime_events_count": len(downtime_events),
                "downtime_events": downtime_events[:10],  # Last 10 events
            }

        except Exception as e:
            logger.error(f"❌ Error getting metrics summary for {service_name}: {e}")
            return {}

    def close(self):
        """Close InfluxDB client connection"""
        try:
            self.client.close()
            logger.info("✅ InfluxDB client closed")
        except Exception as e:
            logger.error(f"❌ Error closing InfluxDB client: {e}")
