document.addEventListener("DOMContentLoaded", () => {
  // --- Hero tilt interaction on the main card ---
  const hero = document.querySelector(".hero-card.hero-main");
  if (hero) {
    hero.addEventListener("mousemove", (e) => {
      const rect = hero.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = (e.clientY - rect.top) / rect.height;

      hero.style.transform = `perspective(900px)
        rotateX(${(0.5 - y) * 6}deg)
        rotateY(${(x - 0.5) * 6}deg)
        translateY(-2px)`;
    });

    hero.addEventListener("mouseleave", () => {
      hero.style.transform = "none";
    });
  }

  // --- Price trend chart on home page ---
  const chartCanvas = document.getElementById("priceTrendChart");
  if (chartCanvas && window.Chart) {
    fetch("/static/data/price_trend.json")
      .then((res) => res.json())
      .then((data) => {
        const labels = data.map((d) => d.year);
        const values = data.map((d) => d.resale_price);

        new Chart(chartCanvas, {
          type: "line",
          data: {
            labels,
            datasets: [
              {
                data: values,
                fill: false,
                tension: 0.25,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label: (ctx) =>
                    `Median: $${ctx.parsed.y.toLocaleString()}`,
                },
              },
            },
            scales: {
              x: {
                ticks: { font: { size: 11 } },
                grid: { display: false },
              },
              y: {
                ticks: {
                  font: { size: 11 },
                  callback: (value) => `$${value / 1000}K`,
                },
              },
            },
          },
        });
      })
      .catch((err) => {
        console.error("Failed to load price trend data", err);
      });
  }
});
