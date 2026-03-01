using MovieApi.Models;

namespace MovieApi.Services
{
    public class MovieService
    {
        private readonly List<Movie> _movies;

        public MovieService()
        {
            _movies = new List<Movie>
            {
                new Movie { Id = 1, Title = "Oppenheimer", Year = 2023, Genre = "Drama", Rating = 8.4, Director = "Christopher Nolan" },
                new Movie { Id = 2, Title = "Jawan", Year = 2023, Genre = "Action", Rating = 7.2, Director = "Atlee" },
                new Movie { Id = 3, Title = "Inception", Year = 2010, Genre = "Sci-Fi", Rating = 8.8, Director = "Christopher Nolan" },
                new Movie { Id = 4, Title = "Avengers", Year = 2012, Genre = "Action", Rating = 8.0, Director = "Joss Whedon" },
                new Movie { Id = 5, Title = "Interstellar", Year = 2014, Genre = "Sci-Fi", Rating = 8.6, Director = "Christopher Nolan" }
            };
        }

        public IEnumerable<Movie> GetMovies(MovieFilter filter)
        {
            var query = _movies.AsQueryable();

            if (filter.Year.HasValue)
                query = query.Where(m => m.Year == filter.Year.Value);

            if (!string.IsNullOrEmpty(filter.Genre))
                query = query.Where(m => m.Genre.ToLower() == filter.Genre.ToLower());

            if (filter.MinRating.HasValue)
                query = query.Where(m => m.Rating >= filter.MinRating.Value);

            if (!string.IsNullOrEmpty(filter.Director))
                query = query.Where(m => m.Director.ToLower().Contains(filter.Director.ToLower()));

            return query.ToList();
        }
    }
}