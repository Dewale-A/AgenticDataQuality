"""Data Quality Assessment Crew Orchestration."""
from crewai import Crew, Process

from src.agents.dq_agents import (
    create_profiler_agent,
    create_validator_agent,
    create_anomaly_detector_agent,
    create_report_writer_agent,
    create_senior_editor_agent,
)
from src.tasks.dq_tasks import (
    create_profiling_task,
    create_validation_task,
    create_anomaly_task,
    create_report_task,
    create_polish_task,
)


class DataQualityCrew:
    """Data Quality Assessment Crew."""

    def __init__(self, data_file: str, cde_config: str = "", polish: bool = False):
        """Initialize the Data Quality Crew.
        
        Args:
            data_file: Path to the data file to assess
            cde_config: Path to the CDE configuration file (optional)
            polish: Whether to include Senior Editor for executive polish
        """
        self.data_file = data_file
        self.cde_config = cde_config
        self.polish = polish
        
        # Create core agents
        self.profiler = create_profiler_agent()
        self.validator = create_validator_agent()
        self.anomaly_detector = create_anomaly_detector_agent()
        self.report_writer = create_report_writer_agent()
        
        # Create core tasks
        self.profiling_task = create_profiling_task(
            self.profiler, data_file, cde_config
        )
        self.validation_task = create_validation_task(
            self.validator, data_file, cde_config
        )
        self.anomaly_task = create_anomaly_task(
            self.anomaly_detector, data_file
        )
        self.report_task = create_report_task(
            self.report_writer, data_file
        )
        
        # Set task context - report task uses all previous outputs
        self.report_task.context = [
            self.profiling_task,
            self.validation_task,
            self.anomaly_task,
        ]
        
        # Optional: Add Senior Editor for polish
        if self.polish:
            self.senior_editor = create_senior_editor_agent()
            self.polish_task = create_polish_task(
                self.senior_editor, data_file
            )
            # Polish task uses the draft report as context
            self.polish_task.context = [self.report_task]

    def create_crew(self) -> Crew:
        """Create and return the Data Quality Crew."""
        # Build agent list
        agents = [
            self.profiler,
            self.validator,
            self.anomaly_detector,
            self.report_writer,
        ]
        
        # Build task list
        tasks = [
            self.profiling_task,
            self.validation_task,
            self.anomaly_task,
            self.report_task,
        ]
        
        # Add editor if polish is enabled
        if self.polish:
            agents.append(self.senior_editor)
            tasks.append(self.polish_task)
        
        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

    def run(self) -> str:
        """Run the Data Quality Assessment.
        
        Returns:
            The final assessment report as a string
        """
        crew = self.create_crew()
        result = crew.kickoff()
        return result
