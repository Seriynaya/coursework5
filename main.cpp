#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <set>
#include <algorithm>
#include <sstream>
#include <optional>
#include <ranges>
#include <ctime>

struct Post {
    int id;
    int author_id;
    std::string title;
    std::string content;
    std::string tags; // comma-separated: "c++,algo,graph"
    int views;
    std::time_t created;
};

// split(s, delim) -> {t_1, t_2, ..., t_k}
[[nodiscard]] auto split(std::string_view s, char delim) -> std::vector<std::string> {
    std::vector<std::string> tokens;
    std::string tok;
    std::istringstream iss{std::string(s)};
    while (std::getline(iss, tok, delim)) {
        const auto start = tok.find_first_not_of(' ');
        const auto end = tok.find_last_not_of(' ');
        if (start != std::string::npos)
            tokens.emplace_back(tok.substr(start, end - start + 1));
    }
    return tokens;
}

// tag_set(post) = {t : t in split(post.tags, ',')}
[[nodiscard]] auto tag_set(const Post& p) -> std::set<std::string> {
    auto v = split(p.tags, ',');
    return {std::make_move_iterator(v.begin()), std::make_move_iterator(v.end())};
}

// {p in P : tag in tag_set(p)}
[[nodiscard]] auto filter_by_tag(const std::vector<Post>& posts, std::string_view tag)
    -> std::vector<Post> {
    std::vector<Post> result;
    const std::string tag_str{tag};
    for (const auto& p : posts) {
        if (const auto ts = tag_set(p); ts.contains(tag_str))
            result.push_back(p);
    }
    return result;
}

// {p in P : query_tags subset of tag_set(p)}
[[nodiscard]] auto filter_by_tags_all(const std::vector<Post>& posts,
                                       const std::set<std::string>& query_tags)
    -> std::vector<Post> {
    std::vector<Post> result;
    for (const auto& p : posts) {
        const auto ts = tag_set(p);
        const bool ok = std::ranges::all_of(query_tags,
            [&ts](const std::string& qt) { return ts.contains(qt); });
        if (ok) result.push_back(p);
    }
    return result;
}

// partial_sort top-K by views desc: O(n log K)
[[nodiscard]] auto top_k_by_views(std::vector<Post> posts, int k) -> std::vector<Post> {
    k = std::min(k, static_cast<int>(posts.size()));
    std::ranges::partial_sort(posts, posts.begin() + k,
        [](const Post& a, const Post& b) { return a.views > b.views; });
    posts.resize(k);
    return posts;
}

// find post by id, nullopt if not found
[[nodiscard]] auto find_post(const std::vector<Post>& posts, int id)
    -> std::optional<Post> {
    for (const auto& p : posts) {
        if (p.id == id) return p;
    }
    return std::nullopt;
}

// pi[i] = max{k<i : P[0..k-1] = P[i-k..i-1]}, O(m)
[[nodiscard]] auto kmp_failure(std::string_view pattern) -> std::vector<int> {
    const int m = static_cast<int>(pattern.size());
    std::vector<int> pi(m, 0);
    int k = 0;
    for (int i = 1; i < m; ++i) {
        while (k > 0 && pattern[k] != pattern[i])
            k = pi[k - 1];
        if (pattern[k] == pattern[i]) ++k;
        pi[i] = k;
    }
    return pi;
}

// KMP: O(n+m)
[[nodiscard]] auto kmp_search(std::string_view text, std::string_view pattern)
    -> std::vector<int> {
    std::vector<int> result;
    if (pattern.empty()) return result;
    const auto pi = kmp_failure(pattern);
    const int n = static_cast<int>(text.size());
    const int m = static_cast<int>(pattern.size());
    int q = 0;
    for (int i = 0; i < n; ++i) {
        while (q > 0 && pattern[q] != text[i])
            q = pi[q - 1];
        if (pattern[q] == text[i]) ++q;
        if (q == m) {
            result.push_back(i - m + 1);
            q = pi[q - 1];
        }
    }
    return result;
}

// f(t) = |{p in P : t in tag_set(p)}|
[[nodiscard]] auto tag_frequency(const std::vector<Post>& posts)
    -> std::unordered_map<std::string, int> {
    std::unordered_map<std::string, int> freq;
    for (const auto& p : posts) {
        for (auto ts = tag_set(p); auto& t : ts)
            ++freq[std::move(t)];
    }
    return freq;
}

void print_post(const Post& p) {
    std::cout << "  [" << p.id << "] \"" << p.title << "\" by:" << p.author_id
              << " views:" << p.views << " tags:{" << p.tags << "}\n";
}

int main() {
    // |P| = 12
    std::vector<Post> posts = {
        {1,  1, "Intro to Graphs",           "Graph theory basics covering BFS and DFS traversals", "algo,graph",         1500, 1710000000},
        {2,  2, "Django REST Framework",      "Building REST APIs with DRF serializers and views",   "python,django,web",   3200, 1710100000},
        {3,  1, "Dynamic Programming Guide",  "DP patterns: knapsack, LCS, edit distance",          "algo,dp",            4100, 1710200000},
        {4,  3, "CSS Grid Layout",            "Modern CSS grid techniques and responsive design",    "web,css",             800, 1710300000},
        {5,  2, "Python Type Hints",          "Using mypy and type annotations in Python 3.12",     "python,typing",      2100, 1710400000},
        {6,  1, "Segment Trees",              "Segment tree with lazy propagation for range queries","algo,ds",            2800, 1710500000},
        {7,  3, "React Hooks Deep Dive",      "useState, useEffect, and custom hooks patterns",     "web,react,js",       5000, 1710600000},
        {8,  2, "Django ORM Optimization",    "QuerySet tricks: select_related, prefetch_related",  "python,django,db",   3800, 1710700000},
        {9,  1, "Network Flow Algorithms",    "Max flow, min cut, and bipartite matching",          "algo,graph,flow",    1200, 1710800000},
        {10, 4, "Machine Learning Basics",    "Linear regression gradient descent and loss functions","python,ml",         6000, 1710900000},
        {11, 2, "Django Middleware",           "Custom middleware for authentication and logging",   "python,django,web",  1900, 1711000000},
        {12, 1, "Algorithm Tips",             "Fast I/O, common patterns, and strategies",          "algo",               4500, 1711100000},
    };

    std::cout << "All posts (" << posts.size() << "):\n";
    for (const auto& p : posts) print_post(p);
    std::cout << "\n";

    // {p in P : "algo" in tag_set(p)}
    const auto algo_posts = filter_by_tag(posts, "algo");
    std::cout << "Posts with tag 'algo' (|result|=" << algo_posts.size() << "):\n";
    for (const auto& p : algo_posts) print_post(p);
    std::cout << "\n";

    // {p in P : {"python","django"} subset of tag_set(p)}
    const std::set<std::string> q_tags = {"python", "django"};
    const auto django_posts = filter_by_tags_all(posts, q_tags);
    std::cout << "Posts with tags {'python','django'} (|result|=" << django_posts.size() << "):\n";
    for (const auto& p : django_posts) print_post(p);
    std::cout << "\n";

    // partial_sort O(n log K), K=5
    const auto top5 = top_k_by_views(posts, 5);
    std::cout << "Top 5 by views:\n";
    for (const auto& p : top5) print_post(p);
    std::cout << "\n";

    // find_post by id
    if (const auto found = find_post(posts, 7)) {
        std::cout << "find_post(7):\n";
        print_post(*found);
        std::cout << "\n";
    }

    // KMP: O(n+m)
    constexpr std::string_view pattern = "Django";
    std::cout << "KMP search for \"" << pattern << "\" in content:\n";
    std::string pat_lower{pattern};
    std::ranges::transform(pat_lower, pat_lower.begin(), ::tolower);
    for (const auto& p : posts) {
        std::string content_lower = p.content;
        std::ranges::transform(content_lower, content_lower.begin(), ::tolower);
        const auto positions = kmp_search(content_lower, pat_lower);
        if (!positions.empty()) {
            std::cout << "  [" << p.id << "] \"" << p.title << "\" -> positions: ";
            for (std::size_t i = 0; i < positions.size(); ++i) {
                if (i) std::cout << ", ";
                std::cout << positions[i];
            }
            std::cout << "\n";
        }
    }
    std::cout << "\n";

    // f(t) = |{p in P : t in tag_set(p)}|
    auto freq = tag_frequency(posts);
    std::vector<std::pair<std::string, int>> freq_vec(
        std::make_move_iterator(freq.begin()),
        std::make_move_iterator(freq.end()));
    std::ranges::sort(freq_vec, [](const auto& a, const auto& b) {
        return a.second > b.second;
    });
    std::cout << "Tag frequency:\n";
    for (const auto& [tag, cnt] : freq_vec) {
        std::cout << "  " << tag << ": " << cnt << "\n";
    }

    return 0;
}
