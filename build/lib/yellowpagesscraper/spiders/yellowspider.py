import scrapy


class YellowspiderSpider(scrapy.Spider):
    name = "yellowspider"
    allowed_domains = ["www.yellowpages.com"]
    start_urls = ["https://www.yellowpages.com/categories/"]

    def parse(self, response):
        main_categories = response.css('.main-content .row-content .row')
        for main_category in main_categories:
            # print("*************************")
            # print(main_category.css('h2::text').get())
            main_category_name = main_category.css('h2::text').get()
            sub_categories = main_category.css('.expand-area a')
            for sub_category in sub_categories:
                sub_category_name = sub_category.css('::text').get()
                sub_category_link = sub_category.css('::attr(href)').get()

                yield response.follow(sub_category_link, callback=self.parse_sub_category, meta={
                    'main-category': main_category_name,
                    'sub-category': sub_category_name,
                    'sub-category-link': sub_category_link
                })

    def parse_sub_category(self, response):
        states = response.css('.main-content .row-content .row')
        for state in states:
            state_name = state.css('::text').get()
            locations = state.css('.expand-area .column a')

            for location in locations:
                location_name = location.css('::text').get()
                location_link = location.css('::attr(href)').get()
                # print('********************')
                # print(location_link)
                location_link = 'https://www.yellowpages.com' + location_link
                yield response.follow(location_link, callback=self.parse_location, meta={
                    'state': state_name,
                    'location': location_name,
                    'location-link': location_link,
                    'main-category': response.meta['main-category'],
                    'sub-category': response.meta['sub-category'],
                    'sub-category-link': response.meta['sub-category-link']
                })

    # def parse_location(self, response):
    #     businesses = response.css('.search-results .result .business-name')

    #     for business in businesses:
    #         business_name = business.css('::text').get()
    #         # print('**************************************')
    #         # print(business_name)
    #         business_link = business.css('::attr(href)').get()
    #         business_link = 'https://www.yellowpages.com' + business_link
    #         yield response.follow(business_link, callback=self.parse_business, meta={
    #             'business-name': business_name,
    #             'business-link': business_link,
    #             'main-category': response.meta['main-category'],
    #             'sub-category': response.meta['sub-category'],
    #             'sub-category-link': response.meta['sub-category-link'],
    #             'state': response.meta['state'],
    #             'location': response.meta['location'],
    #             'location-link': response.meta['location-link']
    #         })
    #     print('*************************************')
    #     print(response.css('.pagination .disabled::text').get())
    #     print('*************************************')

    def parse_location(self, response):
        businesses = response.css('.search-results .result .business-name')

        for business in businesses:
            business_name = business.css('::text').get()
            business_link = business.css('::attr(href)').get()
            business_link = 'https://www.yellowpages.com' + business_link
            yield response.follow(business_link, callback=self.parse_business, meta={
                'business-name': business_name,
                'business-link': business_link,
                'main-category': response.meta['main-category'],
                'sub-category': response.meta['sub-category'],
                'sub-category-link': response.meta['sub-category-link'],
                'state': response.meta['state'],
                'location': response.meta['location'],
                'location-link': response.meta['location-link']
            })

        next_page = response.css('.pagination .next::attr(href)').get()

        if next_page is not None:
            next_page = 'https://www.yellowpages.com' + next_page
            print('==========================================')
            print(next_page)
            with open('pages.txt', 'a') as file:
                file.write(next_page)
                file.write('\n')
            print('==========================================')

            yield response.follow(next_page, callback=self.parse_location, meta={
                'main-category': response.meta['main-category'],
                'sub-category': response.meta['sub-category'],
                'sub-category-link': response.meta['sub-category-link'],
                'state': response.meta['state'],
                'location': response.meta['location'],
                'location-link': response.meta['location-link']
            })

        # Handling pagination
        # next_page = response.css('.pagination .next::attr(href)').get()

        # if next_page is not None:
        #     next_page_link = 'https://www.yellowpages.com' + next_page
        #     print('*******************************')
        #     print(next_page_link)
        #     print('*******************************')
        #     # with open('pages.txt', 'a') as file:
        #     #     file.write(next_page_link)
        #     #     file.write('\n')

        #     yield response.follow(next_page_link, callback=self.parse_location, meta={
        #         'main-category': response.meta['main-category'],
        #         'sub-category': response.meta['sub-category'],
        #         'sub-category-link': response.meta['sub-category-link'],
        #         'state': response.meta['state'],
        #         'location': response.meta['location'],
        #         'location-link': response.meta['location-link']
        #     })

    def parse_business(self, response):
        yield {
            'business-name': response.meta['business-name'],
            'business-ylink': response.meta['business-link'],
            'slogan': response.css('#business-info .slogan::text').get(),
            'general-info': response.css('#business-info .general-info::text').get(),
            'email-business': response.css('#business-info .email-business ::attr(href)').get(),
            'business-history': response.css('#business-info .description::text').get(),
            'bbb-rating': response.css('#business-info .bbb-rating .bbb-no-link::text').get(),
            'bbb-link': response.css('#business-info .bbb-rating .bbb-link::attr(href)').get(),
            'service-products': response.css('#business-info .features-services::text').get(),
            'brands': response.css('#business-info .brands::text').get(),
            'payment-method': response.css('#business-info .payment::text').get(),
            'location-description': response.css('#business-info .location-description::text').get(),
            'amenities': response.css('#business-info .amenities::text').get(),
            'other-links': [link.css('.other-link::text').get() for link in response.css('#business-info .weblinks p')],
            'social-links': [link.css('::attr(href)').get() for link in response.css('#business-info .social-links a')],
            'categories': [category.css('::attr(href)').get() for category in response.css('#business-info .categories a')],
            'other-information': [info.css('::text').get() for info in response.css('business-info .other-information p')],
            'website-link': response.css('.inner-section .website-link ::attr(href)').get(),
            'location-link': response.css('.inner-section .directions ::attr(href)').get(),
            'location-address': response.css('.inner-section .address span::text').get(),
            'phone': response.css('.inner-section .phone ::attr(href)').get(),
            'main-category': response.meta['main-category'],
            'sub-category': response.meta['sub-category'],
            'sub-category-link': response.meta['sub-category-link'],
            'state': response.meta['state'],
            'las': response.meta['location'],
            'las-link': response.meta['location-link'],
        }
