.. title: Blog Statistics
.. slug: stats
.. date: 2026-11-12 07:00:00 UTC+03:00
.. tags: 
.. category: 
.. link: 
.. description: Public views and reactions statistics across all blog articles.
.. type: text

Public views and reactions statistics across all blog articles. Data is updated in real time.

.. raw:: html

    <div id="blog-stats-container" style="margin-top: 20px;">
        <p>Loading statistics...</p>
    </div>

    <script>
        const apiUrl = window.location.port === '8888' ? 'http://127.0.0.1:8083' : (window.location.port === '8000' ? 'http://127.0.0.1:8082' : '');

        async function loadBlogStats() {
            try {
                const response = await fetch(apiUrl + '/api/stats');
                if (!response.ok) throw new Error('Failed to load statistics');
                const stats = await response.json();
                
                if (!stats || stats.length === 0) {
                    document.getElementById('blog-stats-container').innerHTML = '<p>No statistics available yet.</p>';
                    return;
                }

                let html = '<div class="table-responsive"><table class="table table-striped table-bordered" style="width:100%; background: white;">';
                html += '<thead><tr><th>Article / Slug</th><th>👁 Views</th><th>👍 Likes</th><th>❤️ Hearts</th><th>🔥 Fire</th><th>👏 Claps</th><th>💩 Poops</th><th>Total Reactions</th></tr></thead><tbody>';
                
                stats.forEach(item => {
                    html += `<tr>
                        <td><a href="${item.slug}">${item.slug}</a></td>
                        <td><strong>${item.views}</strong></td>
                        <td>${item.likes}</td>
                        <td>${item.heart}</td>
                        <td>${item.fire}</td>
                        <td>${item.clap}</td>
                        <td>${item.poop}</td>
                        <td><strong>${item.total_reactions}</strong></td>
                    </tr>`;
                });
                
                html += '</tbody></table></div>';
                document.getElementById('blog-stats-container').innerHTML = html;
            } catch (e) {
                console.error(e);
                document.getElementById('blog-stats-container').innerHTML = '<p style="color: red;">Failed to load statistics. Make sure the stats service is running.</p>';
            }
        }
        loadBlogStats();
    </script>
