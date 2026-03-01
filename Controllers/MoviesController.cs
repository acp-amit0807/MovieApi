using Microsoft.AspNetCore.Mvc;
using MovieApi.Models;
using MovieApi.Services;

namespace MovieApi.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class MoviesController : ControllerBase
    {
        private readonly MovieService _movieService;

        public MoviesController(MovieService movieService)
        {
            _movieService = movieService;
        }

        [HttpGet]
        public IActionResult GetMovies([FromQuery] MovieFilter filter)
        {
            var movies = _movieService.GetMovies(filter);
            return Ok(movies);
        }
    }
}