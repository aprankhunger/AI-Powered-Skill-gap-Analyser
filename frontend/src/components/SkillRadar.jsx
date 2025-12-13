import React from "react";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import { Radar } from "react-chartjs-2";

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const SkillRadar = ({ skills = [], title = "Skills Overview" }) => {
  // If no skills, show placeholder
  if (!skills || skills.length === 0) {
    return (
      <div className="bg-white/5 rounded-xl p-6 text-center">
        <p className="text-gray-400">No skill data available</p>
      </div>
    );
  }

  // Take top 8 skills for radar chart
  const topSkills = skills.slice(0, 8);
  
  const data = {
    labels: topSkills,
    datasets: [
      {
        label: "Proficiency",
        data: topSkills.map(() => Math.floor(Math.random() * 40) + 60), // Simulated proficiency
        backgroundColor: "rgba(59, 130, 246, 0.2)",
        borderColor: "rgba(59, 130, 246, 1)",
        borderWidth: 2,
        pointBackgroundColor: "rgba(59, 130, 246, 1)",
        pointBorderColor: "#fff",
        pointHoverBackgroundColor: "#fff",
        pointHoverBorderColor: "rgba(59, 130, 246, 1)",
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    scales: {
      r: {
        angleLines: {
          color: "rgba(255, 255, 255, 0.1)",
        },
        grid: {
          color: "rgba(255, 255, 255, 0.1)",
        },
        pointLabels: {
          color: "rgba(255, 255, 255, 0.8)",
          font: {
            size: 11,
          },
        },
        ticks: {
          display: false,
          beginAtZero: true,
          max: 100,
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
    },
  };

  return (
    <div className="bg-white/5 rounded-xl p-4">
      <h3 className="text-lg font-semibold text-white mb-4 text-center">{title}</h3>
      <div className="max-w-[300px] mx-auto">
        <Radar data={data} options={options} />
      </div>
    </div>
  );
};

export default SkillRadar;
